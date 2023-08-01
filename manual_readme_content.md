
**Prerequisites:**

-   CriticalStack Intel account must be created.
-   At least one CriticalStack Intel sensor must be created with at least one intel feed in its
    collection.
-   CriticalStack Intel client must be installed on a host reachable by this Phantom instance via
    SSH.
-   Phantom API key must be generated for use by this app.

**Phantom Custom Lists Created by this app:**

-   CriticalStack-LastUpdated
-   \<prefix>-ADDR - List of IPs from CriticalStack (1 per asset definition)
-   \<prefix>-DOMAIN - List of domains from CriticalStack (1 per asset definition)
-   \<prefix>-HASH - List of file hashes from CriticalStack (1 per asset definition)

This will create up to 4 Phantom custom lists for each CriticalStack asset defined. One list will be
maintained across all assets, 'CriticalStack-LastUpdated'. The purpose of this list is to keep track
of when this app last pulled from a particular CriticalStack sensor. This is necessary to prevent
rate-limiting by CriticalStack (max: 1 pull per half hour). The other lists will contain the
Domains, IPs, and File Hashes retrieved from CriticalStack, as a local (to Phantom) repository. All
Domain, IP, and Hash lists will be prepended with the 'prefix' designated in the asset definition to
keep track of from which CriticalStack Phantom asset the lists originated.

When 'file reputation', 'domain reputation', or 'ip reputation' are run, the app will first check
the 'CriticalStack-LastUpdated' list for the 'prefix' defined in the asset definition, to see if it
has been longer than half hour since a 'pull' was performed. If there have been longer than 30
minutes in elapsed time, the app will connect to the CriticalStack host, perform the 'pull' and then
upload the results to the corresponding Phantom lists. Then, the corresponding Phantom list will be
checked to see if the ip/file hash/domain exists.

The 'prefix' allows for separate Phantom lists to be created for individual CriticalStack sensors.
It achieves this by prepending each file hash/domain/ip list with this prefix. This allows for users
to create sensors for different purposes if desired.
