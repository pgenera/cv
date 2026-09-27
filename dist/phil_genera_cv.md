# Phil Genera

Infrastructure & Site Reliability Engineering

- Location: Cambridge, MA
- Email: <pg@fivesevenfive.org>
- Phone: +1 (203) 606-4771
- [github.com/pgenera](https://github.com/pgenera)
- [linkedin.com/in/pgenera](https://www.linkedin.com/in/pgenera)

## Summary

Infrastructure engineer with 19 years at Google, roughly fifteen of them as an individual contributor and tech lead across mobile search, media and storage infrastructure, cloud networking, and healthcare systems, and the last four managing small infrastructure teams. Built the first global load balancing for the L7 proxy fronting Google Cloud, and currently responsible for the reliability and safety of footprint operations across Google's internal continuous-delivery infrastructure. Expert at the layer where capacity, traffic management, and failure domains meet, and still writing and shipping systems code outside of work.

## Technical

Java, Python, SQL, and C++, plus a long tail of domain-specific languages, with recent project work in Kotlin and Go. Linux systems work: nftables, policy routing and BGP, docker, btrfs, tcpdump, netcat. Agentic development with Claude Code and Antigravity. Global and regional load software load balancing.

## Experience

### Google (Aug 2007 – Present)

#### Software Engineering Manager, Continuous Delivery Infrastructure (Feb 2024 – Present)

- Manage the team responsible for footprint operations (turn up, turn down, resize, move) across Google's CD infrastructure, which actuates the majority of the datacenter footprint.
- Own the reliability and safety of those actions. The goal is that capacity changes cannot take down the services that depend on them, and that unsafe cases fail closed rather than proceeding. Defined and drove progress on customer-centric SLIs, SLOs, and SLAs.
- Moved footprint changes from operator-driven execution toward automated, continuous actuation, so that the scale and speed of a change is bounded by policy rather than by operator attention, and is easier, safer, and faster.
- Responsible for the oncall team in US-East, training up new members, managing workload with the global team, and giving Incident Command System training annually.

#### Staff Site Reliability Engineer, Site Reliability Engineering Manager, Google for Clinicians (Apr 2021 – Feb 2024)

- SRE lead for Google's short-lived EHR search and longitudinal health-record product (Google for Clinicians), serving one of the largest hospital systems in the United States, delivering streaming record updates, normalization, enrichment and analysis end to end in minutes.
- In addition to ETL indexing and search, the import pipeline added AI enrichments to physician notes and test results. Designed, built, and shipped load balancing and traffic management for the enrichment pipeline, delivering significantly higher reliability, lower operator toil, and resiliency against bad input.
- Took over management of the team in June 2022 while continuing the SRE work. Scope covered HIPAA and related compliance, infrastructure cost, project planning, customer relationships and software engineering productivity.

#### Senior Software Engineer, Google Cloud Networking (Aug 2017 – Apr 2021)

- Built the first global load balancing for Google's internal L7 proxy (CloudPath, sitting between Google Cloud and Google production), a large and high-reliability component of the Google Cloud Platform.
- This load balancing project, with others, enabled traffic grown from XX Gbps to XX Tbps, with higher customer reliability, and lower cost.
- Worked across the proxy and the software-defined networking control plane feeding it, publicly described in *Orion: Google's Software-Defined Networking Control Plane* (NSDI 2021).

#### Senior Site Reliability Engineer, YouTube & Storage Infrastructure (Nov 2012 – Aug 2017)

- Ran the West Coast side of the SRE team operating YouTube's video transcoding pipeline and upload server, which went on to become Google Cloud Storage.
- As tech lead for the upload server, led the infrastructure response to the 2013 Snowden disclosures for the upload server and GCS.
- Shared oncall and operational ownership of YouTube uploads, transcoding, Content ID, and streaming infrastructure.
- Production Readiness Review and SRE onboarding of YouTube Live Streaming infrastructure, which is shared between YouTube, Google Fiber, and YouTube TV.

#### Software Engineer, Mobile Search (Aug 2007 – Nov 2012)

- Invented *Search with My Location*, the blue dot on the mobile search home page, and co-authored the resulting patent with the product manager for the feature.
- Worked on google.com/m, particularly universal and local search, and curated the local search property for several years.
- Tech lead for mobile search infrastructure work, including launching ads on new mobile properties.
- 24x7 oncall rotation, turned up capacity in response to emergencies, handled DoS configuration and response, and led the Production Readiness Review and trained up the SRE team founded to take on this (and other) mobile services.

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

### Home automation and network toys (ongoing)

- [wallbox-ble](https://github.com/pgenera/wallbox-ble) attaches EV chargers to Home Assistant via bluetooth proxies.
- [sundial-ntp](https://github.com/pgenera/sundial-ntp) is a solar-panel disciplined NTP refclock.
- [mpubsub](https://github.com/pgenera/esphome-mpubsub) implements my [defensive publication](https://www.tdcommons.org/dpubs_series/5601) of brokerless Publish/Subscribe, and adds typing and encryption.
- Linux-routed home network with policy-based routing, roughly one VLAN per resident, and an nftables trust-zone ruleset.
- Run IPv4 and IPv6 NTP servers in the public pool, served from AMPRNet (44/8) address space.
- Building my own consoles, monitoring, and alerting for the systems I own, from woodstoves to furnaces to solar arrays.

## Patents and Publications

- [US Patent 9,081,860](https://patents.google.com/patent/US9081860B2/en), *Integration of Device Location into Search* (filed 2008, issued 2015), co-inventor.
- [*Self-Organizing Publish/Subscribe on the Network Edge*](https://www.tdcommons.org/dpubs_series/5601), Technical Disclosure Commons, Art. 5601 (2022).

## Education

- Rensselaer Polytechnic Institute, B.S., Computer Science & Psychology (2001 – 2005)

## Additional

- Amateur radio operator. Volunteers at the Boston Marathon as third-tier communications from a course medical tent, handling medical resupply and sweep bus traffic within the event's incident command structure.
- Powerlifting, running, and long-distance motorcycling.
- Eagle Scout.
