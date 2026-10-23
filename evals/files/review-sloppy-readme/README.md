# 🚀 PulseCheck

## 🌟 Overview

In today's fast-paced digital landscape, monitoring is more important than ever. PulseCheck is a robust, lightweight, and comprehensive uptime monitoring solution that seamlessly empowers teams to stay on top of their services. It's not just a monitoring tool — it's a complete peace-of-mind platform.

## ✨ Key Features

- **Blazing Fast Checks** — PulseCheck runs HTTP checks every 30 seconds by default, ensuring you are always informed.
- **Smart Alerting** — Alerts are sent to Slack or email after 3 consecutive failures, which helps reduce noise and keeps your team focused on what truly matters.
- **Flexible Configuration** — All configuration lives in a single `pulse.yaml` file, making it incredibly easy to get started.

## 🛠️ Getting Started

Getting started with PulseCheck is a breeze! Simply follow these easy steps:

1. First, make sure you have Python 3.12 or newer installed on your machine.
2. Next, install the dependencies by running `make install`.
3. Then, start the development server with `make dev`. The dashboard will be available at http://localhost:8080.
4. Finally, set the `PULSE_SLACK_WEBHOOK` environment variable to enable Slack alerts.

## 💡 Why PulseCheck?

It's important to note that PulseCheck was deliberately designed with simplicity in mind. Rather than overwhelming you with endless options, it focuses on what really matters: knowing when your services are down. Whether you're a solo developer or part of a large team, PulseCheck adapts to your needs.

## 🤝 Contributing

We warmly welcome contributions from the community! Please feel free to open an issue or submit a pull request. Every contribution, no matter how small, makes a difference.

## 📄 License

PulseCheck is proudly released under the MIT License.
