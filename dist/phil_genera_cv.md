# Phil Genera

Infrastructure & Site Reliability Engineer

Latest version: <https://cv.fivesevenfive.org/>. Updated October 2026.

- Location: Beverly, MA
- Email: <pg@fivesevenfive.org>
- Phone: +1 (203) 606-4771
- [github.com/pgenera](https://github.com/pgenera)
- [linkedin.com/in/pgenera](https://www.linkedin.com/in/pgenera)

## Summary

Infrastructure engineer with nineteen years at Google. An expert at the layer where capacity, traffic management, and failure domains meet. Fifteen years as an individual contributor and tech lead across diverse projects such as Electronic Health Record AI enrichment, planet-scale network load balancing, and Google Search with My Location. An additional four years managing small infrastructure teams while still writing and shipping systems code, internally and externally. Built global load balancing for the L7 proxy carrying most storage bits in Google Cloud, and currently responsible for the reliability and safety of footprint operations across Google's internal continuous-delivery infrastructure. Carried the pager for Google Search, YouTube, and Google Cloud Storage; now training an oncall team in the Incident Command System.

## Technical

Java, Python, C++, and SQL, and a long tail of domain-specific languages; recent agentic work in Kotlin and Go with Claude Code and Antigravity. Global and regional software load balancing, networking, and Bluetooth reverse engineering.

## Experience

### Google (Aug 2007 – Present)

#### Software Engineering Manager, Continuous Delivery Infrastructure (Feb 2024 – Present)

- Manage the team of ten responsible for footprint operations (turn up, turn down, resize, move) across Google's CD infrastructure, which actuates the majority of the datacenter footprint, and is on the critical path for Cloud region and zone expansion, AI capacity delivery, and efficiency.
- Led the team through a 79% reduction in failures of those footprint operations. Negotiated, defined, and drove improvements to customer-centric SLIs, SLOs, and SLAs. Own the team's capacity supervision for footprint changes, which halts rollouts if overload is predicted.
- The team sits at the interface between automated capacity planning and actuation, and is moving footprint changes from operator-driven execution to automated, continuous actuation.
- Built agentic workflows for the team: conversational bug filing, hands-off  fixes and code reviews, and automated root-cause analysis.
- Responsible for the oncall team in US-East. Onboarding new members, managing workload with the global team, and training the team on the Incident Command System annually; also a Boston Marathon ICS volunteer.

#### Site Reliability Engineering Manager, Google for Clinicians (Jun 2022 – Feb 2024)

- Took over management of the team of five while continuing SRE work. The scope covered HIPAA and related compliance, infrastructure cost, project planning, customer relationships, and software engineering productivity.

#### Senior Site Reliability Engineer, Google for Clinicians (May 2021 – Jun 2022)

- SRE lead for Google's EHR search and longitudinal health-record product, Google for Clinicians, serving one of the largest hospital systems in the United States. Delivering streaming record updates, normalization, enrichment, and analysis from bedside to serving in minutes.
- In addition to ETL indexing and search, the import pipeline added AI enrichments to physician notes and test results. Designed, built, and shipped load balancing and traffic management for the enrichment pipeline, delivering significantly higher reliability, lower operator toil, and resiliency against bad input.

#### Senior Software Engineer, Google Cloud Networking (Aug 2017 – May 2021)

- Built the first global load balancing for Google's internal L7 proxy (CloudPath, sitting between Google Cloud and Google production), a large and high-reliability component of the Google Cloud Platform.
- This load balancing project, with others, enabled traffic growth from Gbps to Tbps, with higher customer reliability and lower infrastructure cost.
- Landed features across the proxy and software-defined networking data and control planes ([Orion](https://research.google/pubs/orion-googles-software-defined-networking-control-plane/), NSDI 2021).
- Made small contributions to Envoy Proxy's control-plane efficiency.

#### Senior Site Reliability Engineer, Social SRE (May 2014 – Aug 2017)

- Moved to Cambridge, MA, as a tech lead for Social SRE, which ran the Gmail contacts database along with other graph indexing and storage services.
- When the team split into storage and graph halves, led the graph side: storage for all implicit and explicit social graph data, the Zanzibar authorization system ([USENIX ATC 2019](https://www.usenix.org/conference/atc19/presentation/pang)), and a service that ranks contacts by graph distance for suggestions across Google products.

#### Senior Site Reliability Engineer, YouTube & Storage Infrastructure (Nov 2012 – May 2014)

- Ran the West Coast SRE team operating YouTube's video transcoding pipeline and upload server, which went on to become the Google Cloud Storage frontend.
- As tech lead, owned the upload server's SRE response to the 2013 Snowden disclosures, and contributed to the broader GCS infrastructure response.
- Led the Production Readiness Review and SRE onboarding of YouTube Live Streaming infrastructure, which is shared between YouTube, GFiber, and YouTube TV.

#### Software Engineer, Mobile Search (Aug 2007 – Nov 2012)

- Invented *Search with My Location*, the blue dot on the mobile search home page, and co-authored the resulting patent with the product manager for the feature.
- Worked on google.com/m universal and local search; designed and led the local search property.
- Tech lead for mobile search infrastructure work, including launching ads on new mobile properties.
- 24x7 oncall: emergency capacity turnups, DoS response, and the Production Readiness Review. Trained the SRE team founded to take over mobile services.

### Cisco Systems (Jul 2005 – Aug 2007)

#### Software Engineer (Jul 2005 – Aug 2007)

- Built monitoring, diagnostics, and modular plugin tooling in Java for enterprise Linux telephony server clusters.

## Patents and Publications

- [U.S. Patent 9,081,860](https://patents.google.com/patent/US9081860B2/en), “Integration of Device Location into Search,” with J. Siegel (filed 2008, issued 2015).
- “Self-Organizing Publish/Subscribe on the Network Edge,” *Technical Disclosure Commons, Defensive Publications Series*, [Art. 5601](https://www.tdcommons.org/dpubs_series/5601) (2022).

## Personal Projects

### [wearvian](https://github.com/pgenera/wearvian): Wear OS phone key for Rivian R1 vehicles (2026)

- Wear OS app that functions as a Rivian phone key over Bluetooth LE: passive entry and drive enable by proximity, plus lock, frunk, liftgate, window, charge port, and climate commands.
- Reverse engineered and documented the vehicle's phone-key protocol: the pairing handshake, the authenticated ranging heartbeat that passive entry actually keys on rather than OS-level bonding, AES-GCM command framing, and the status stream that drives live lock, closure, charge, and range display.
- Security-first design that works offline: the watch has no internet access and its private key never leaves it; a [companion phone app](https://github.com/pgenera/wearvian-companion) performs the one-time cloud enrollment over the Wear OS Data Layer.

### Embedded systems and network services (ongoing)

- [mpubsub](https://github.com/pgenera/esphome-mpubsub) implements the brokerless Publish/Subscribe from the [defensive publication](https://www.tdcommons.org/dpubs_series/5601), and adds typing and encryption.
- [wallbox-ble](https://github.com/pgenera/wallbox-ble) attaches EV chargers to Home Assistant via Bluetooth proxies.
- IPv4 and IPv6 NTP servers in the public pool, served from AMPRNet (44/8) address space. Hundreds of RPS of time served.
- [sundial-ntp](https://github.com/pgenera/sundial-ntp) is a solar-disciplined NTP refclock.
- Consoles, monitoring, and alerting for everything at home, from woodstoves to furnaces to solar arrays.

## Education

- Rensselaer Polytechnic Institute, B.S., Computer Science & Psychology (2001 – 2005)

## Additional

- Amateur Radio Operator at a Boston Marathon medical tent, handling medical resupply and sweep bus traffic within the Incident Command System. (2016 – Present)
- Amateur radio (W1JV), atomic clocks, frequency measurement, and antique test equipment.
- Powerlifting, running, and endurance motorcycling. Home automation and heating with wood. Eagle Scout.
