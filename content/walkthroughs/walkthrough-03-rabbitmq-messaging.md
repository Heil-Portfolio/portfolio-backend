---
title: "DreamHouse-237 — #3: RabbitMQ & Messaging, and the Night I Found Strangers in My Logs"
slug: dreamhouse237-rabbitmq-messaging
status: draft
tags:
  - RabbitMQ
  - Messaging
  - Event-Driven
  - Security
  - AWS
  - Docker
  - Microservices
objective: Let services stay in sync without ever calling each other directly — and figure out why my broker's logs had connection attempts I never made.
stack: RabbitMQ 3 (management), Pika, Django, Docker Compose, AWS EC2 Security Groups
architecture: Auth Service and User Service exchange events through RabbitMQ queues instead of calling each other's APIs; Publication, Payment, and Commentary follow the same pattern
problems_encountered: RabbitMQ's AMQP port and management UI were reachable from outside the VPC because of how the Docker port mapping and the EC2 security group interacted
lessons_learned:
  - A Docker port mapping like "5672:5672" binds to every interface on the host by default — 'it works on localhost' tells you nothing about who else can reach it
  - A management UI is still a login page. If it's public, it's an attack surface, not a convenience
  - Decoupling services with a queue also decouples your blast radius — for better and for worse
  - Logs are worth reading even when nothing looks broken. Mine weren't 'broken', they were being probed
reading_time: 10
date: 2026-07-31
---

## Services that don't call each other

By the time I got Eureka and the Gateway behaving (walkthrough #2), I had a working request/response system: client hits the Gateway, Gateway resolves the right service, service answers. Clean, synchronous, easy to reason about.

It's also the wrong model for some of what DreamHouse-237 needed to do. When a user signs up through **User Service**, **Auth Service** also needs to know about it — to create the login credentials. But User Service shouldn't have to know Auth Service's address, wait on it, or fail its own request because Auth happened to be slow that day. That's not a routing problem, it's a coupling problem, and the fix isn't a smarter Gateway — it's not calling directly at all.

That's what RabbitMQ is doing in this architecture: services publish events into queues and move on, and whoever cares about that event picks it up whenever they're ready.

## The flow: Auth and User, staying in sync without talking

Here's the queue map as it stands today:

| Queue | Producer | Consumer | Payload & trigger |
|---|---|---|---|
| `user-created` | User Service | Auth Service | `{event_id, email, password_hash, role, user_service_id, cni_recto, cni_verso}` — on every signup |
| `user-auth-ack` | Auth Service | User Service | `{event, user_service_id, user_auth_id}` — acknowledgment after AuthUser is created |
| `user-verified` | User Service | Auth Service | `{user_auth_id, is_verified: true}` — after email verification |
| `user-email-queue` | Auth Service | User Service | Email sync after login — keeps both sides coherent |
| `user-identified` | Identity Service | User Service | `{email, nom, prenom, numero_cni, status, requested_role}` — result of OCR / admin validation |
| `payment-queue` | Publication Service | Payment Service | `{correlationId, publicationId, userId, amount, email, phone}` — CamPay payment initiation |
| `payment-status` | Payment Service | Publication Service | `{correlationId, publicationId, status, reference}` — CamPay webhook result |
| `publication-deleted` | Publication Service | Commentary Service | `{publication_id}` — cleanup of orphaned comments |

The Auth/User pair is the one worth walking through in detail, because it's a full round trip. Here's the consumer that picks up `user_created` on the Auth side:

```python
def handle_user_created(ch, method, properties, body):
    _close_db_connections()

    from ..models import AuthUser
    from .message_publisher import RabbitMQPublisher

    data = json.loads(body)
    email = data.get("email")
    user_service_id = data.get("user_service_id")

    if AuthUser.objects.filter(email=email).exists():
        auth_user = AuthUser.objects.get(email=email)
        # already exists — still ack, still keep user_service_id in sync
    else:
        auth_user = AuthUser(email=email, role=data.get("role", "client"))
        auth_user.set_password(data.get("password"))
        auth_user.save()

    publisher = RabbitMQPublisher(queue="user_auth_ack")
    publisher.publish_message({
        "event": "user.auth_created",
        "user_service_id": str(user_service_id),
        "user_auth_id": str(auth_user.id),
    })

    ch.basic_ack(delivery_tag=method.delivery_tag)
```

Signup creates a `user_created` event → Auth consumes it, creates the credentials, and publishes `user_auth_ack` back → User Service picks that up and knows the loop closed. Neither service ever calls the other's API directly. If Auth is down for five minutes, the message just waits in the queue instead of the signup request failing outright.

> 💭 One detail I almost glossed over, buried right at the top of the consumer: `_close_db_connections()`, called before every single message. RDS MySQL closes idle connections after a timeout, and a long-running consumer process can easily hold on to a stale connection between messages. Without that line, the consumer looks fine for a while and then starts silently failing to save anything — a bug I'd rather mention here than relive in its own walkthrough.

## The night I found strangers in my logs

This part of the story isn't about the messaging logic — it's about the box the messaging logic runs in.

RabbitMQ, like everything else in this project, runs in Docker:

```yaml
messagebroker-service:
  image: rabbitmq:3-management
  container_name: messagebroker-service
  restart: always
  ports:
    - "5672:5672"
    - "15672:15672"
  environment:
    RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
    RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
```

Nothing here looks wrong at a glance. It's the same shape as every other `ports:` block in the project. That's exactly what made it dangerous.

A Docker port mapping written as `"5672:5672"` — with no host address specified — binds to **every network interface on the host**, not just `localhost`. On a laptop behind a home router that's rarely a problem. On an EC2 instance with a public IP, it means the container is reachable from outside the box the moment the security group allows it through. And `15672` isn't just the AMQP broker — it's the full **management UI**, a real login page, sitting behind nothing but `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS`.

I found out this was actually happening the boring way: **reading the logs**. RabbitMQ was logging connection attempts I hadn't made, from clients I didn't recognize, hitting the broker from outside anything my own services would ever originate from. Nothing dramatic — no alert, no scanner, no "you've been hacked" banner. Just entries that didn't belong to me, sitting quietly in output I could easily have ignored.

> 🛡️ This is the same lesson from walkthrough #1's "hacker" scare, but the other direction: last time, a scary-looking signal turned out to be nothing. This time, an unremarkable-looking log line turned out to be real. Both times, the only way to tell the difference was to actually go read the evidence instead of guessing from the vibe of the situation.

### The fix

Two changes, applied together:

1. **Restricted the EC2 security group** so `5672` and `15672` were no longer reachable from `0.0.0.0/0` — only from the internal ranges that actually needed to talk to the broker.
2. **Locked the management UI down further, to my own machine specifically** — since `15672` is an admin interface, not something any service needs to reach from outside the VPC at all, and it didn't need to be broadly available even internally.

The messaging logic itself — the queues, the consumers, the Auth/User round trip — didn't change at all. The whole fix lived one layer below the application code, in the security group and in how the ports were exposed.

---

## What I learned from all of this

- **A Docker port mapping is a network decision, not a convenience shortcut.** `"5672:5672"` reads like "make this available," and it's easy to stop thinking about it the moment `localhost` works.
- **A management UI is still a login page.** It's tempting to treat admin dashboards as "internal by nature" because they *feel* like tooling rather than a real service — they're not, and they need the same scrutiny as anything else exposed to the internet.
- **Decoupling has a security dimension, not just an architectural one.** Queues remove tight coupling between services, but the broker connecting them becomes a single point that, if exposed, gives an outsider a view into events from every service that publishes to it.
- **Boring logs are worth reading.** Nothing about this incident announced itself. It looked exactly like the kind of output you scroll past on a normal day.

## What's next

With messaging decoupled and the broker actually secured, the next walkthrough goes back up a layer — into how a single JWT travels safely across every one of these services without each one having to re-authenticate the user from scratch.

- 🚪 **Gateway, JWT & Security** — how one token safely travels across the whole system
- 🐛 **The Django/Gunicorn deadlock** — my worst bug, and how I finally tracked it down

On to the next one 👇
