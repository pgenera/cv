# Phil Genera

Infrastructure & Site Reliability Engineering

- Location: Cambridge, MA
- Email: <pg@fivesevenfive.org>
- [github.com/pgenera](https://github.com/pgenera)
- [linkedin.com/in/pgenera](https://www.linkedin.com/in/pgenera)

## Summary

Infrastructure engineer with 19 years at Google, roughly fifteen of them as an individual contributor and tech lead across mobile search, media and storage infrastructure, cloud networking, and healthcare systems, and the last four managing small infrastructure teams. Built the first global load balancing for the L7 proxy fronting Google Cloud, and currently responsible for the reliability and safety of footprint operations across Google's internal continuous-delivery infrastructure. Comfortable at the layer where capacity, traffic management, and failure domains meet, and still writing and shipping systems code outside of work.

## Technical

Java, Python, and C++, plus a long tail of domain-specific languages, with recent project work in Kotlin and Go. Routine Linux systems work: nftables, policy routing and BGP, btrfs, tcpdump, netcat. Agentic development with Claude Code and Antigravity. Minor contributions to Envoy.

## Experience

### Google (Aug 2007 – Present)

#### Software Engineering Manager, Continuous Delivery Infrastructure (Feb 2024 – Present)

- Manage the team responsible for footprint operations (turn up, turn down, resize, move) across Google's internal continuous-delivery infrastructure, which actuates the majority of the production footprint.
- Own the reliability and safety of those actions. The goal is that routine capacity changes cannot take down the services that depend on them, and that unsafe cases fail closed rather than proceeding.
- Work on moving footprint changes from operator-driven execution toward automated, gated actuation, so that the scale of a change is bounded by policy rather than by operator attention.

#### Senior Site Reliability Engineer, then Site Reliability Engineering Manager, Google for Clinicians (Apr 2021 – Feb 2024)

- SRE for an EHR search and longitudinal health-record research platform serving one of the largest hospital systems in the United States, delivering streaming record updates, normalization, and analysis end to end in minutes.
- Took over management of the team in June 2022 while continuing the SRE work. Scope covered HIPAA and related compliance, infrastructure cost, and software engineering productivity.

#### Senior Software Engineer, Google Cloud Networking (Aug 2017 – Apr 2021)

- Built the first global load balancing for Google's L7 proxy, the tier sitting between Google Cloud and Google production, a large and high-visibility system carrying external traffic into the platform.
- Worked across the proxy and the software-defined networking control plane feeding it, publicly described in *Orion: Google's Software-Defined Networking Control Plane* (NSDI 2021).

#### Senior Site Reliability Engineer, YouTube & Storage Infrastructure (Nov 2012 – Aug 2017)

- Ran the west-coast side of the SRE team operating YouTube's video transcoding pipeline and upload server. The upload server went on to become Google Cloud Storage.

#### Software Engineer, Mobile Search (Aug 2007 – Nov 2012)

- Invented *Search with My Location*, the blue dot on the mobile search home page, and co-authored the resulting patent with the product manager for the feature.
- Worked on google.com/m, particularly universal and local search, and curated the local search property for several years.
- Tech lead for mobile search infrastructure work, including launching ads on new mobile properties.

### Cisco Systems (Jul 2005 – Aug 2007)

#### Software Engineer (Jul 2005 – Aug 2007)

- Built monitoring, diagnostics, and modular plugin tooling in Java for enterprise Linux server clusters.

## Personal Projects

### [wearvian](https://github.com/pgenera/wearvian): Wear OS phone key for Rivian R1 vehicles (2026)

- Wear OS app that functions as a Rivian phone key over Bluetooth LE: passive entry and drive enable by proximity, plus lock, frunk, liftgate, window, charge port, and climate commands. Confirmed working on a Gen-1 R1S.
- Reverse engineered the vehicle's phone-key protocol and documented it: the pairing handshake, the authenticated ranging heartbeat that passive entry actually keys on rather than OS-level bonding, AES-GCM command framing, and the status stream that drives live lock, closure, charge, and range display.
- Wrote `core-crypto`, a standalone Kotlin/JVM module implementing secp256r1, ECDH, HKDF-SHA256, HMAC, and AES-GCM command frames, verified against known-answer parity tests.
- Built for offline operation and key custody: the watch holds no `INTERNET` permission and its private key never leaves the device, with a [companion phone app](https://github.com/pgenera/wearvian-companion) performing the one-time cloud enrollment over the Wear OS Data Layer.
- Power-saving passive mode releases the wake lock and tears down the radio when idle, with a hardware-offloaded scan rebuilding the link on approach.

### [mpubsub](https://github.com/pgenera/esphome-mpubsub): brokerless IPv6 multicast pub/sub transport (2026)

- Publish/subscribe transport with no broker: each topic maps deterministically to an IPv6 multicast group derived from a SHA-256 of the topic name, so publishers and subscribers rendezvous without coordination and the fabric survives losing the WAN.
- Wire protocol with a 12-byte header, CRC-32 topic disambiguation, and optional authenticated encryption, shipped as an ESPHome component in C++, a Home Assistant integration in Python, a Go bridge to MQTT, and a Python reference implementation.

### Home network and radio infrastructure (ongoing)

- Linux-routed network with policy-based routing, inter-VLAN routing across segments drawn well past the point of necessity (roughly one VLAN per resident), an nftables trust-zone ruleset, IPv6 tunneling, and BGP-announced AMPRNet (44/8) address space.
- Survey-calibrated u-blox GPS timing receiver on gpsd, with custom Python tooling for the UBX configuration the standard utilities do not reach.

## Patents and Publications

- [US Patent 9,081,860](https://patents.google.com/patent/US9081860B2/en), *Integration of Device Location into Search* (filed 2008, issued 2015), co-inventor.
- [*Self-Organizing Publish/Subscribe on the Network Edge*](https://www.tdcommons.org/dpubs_series/5601), Technical Disclosure Commons, Art. 5601 (2022).

## Education

- Rensselaer Polytechnic Institute, B.S., Computer Science & Psychology (2001 – 2005)

## Additional

- Amateur radio operator. Volunteers at the Boston Marathon as third-tier communications from a course medical tent, handling medical resupply and sweep bus traffic within the event's incident command structure.
- Powerlifting, running, and long-distance motorcycling.
- Eagle Scout.
