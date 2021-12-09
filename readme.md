[comment]: # "Auto-generated SOAR connector documentation"
# CriticalStack Intel

Publisher: AvantGarde Partners  
Connector Version: 1\.0\.6  
Product Vendor: CriticalStack  
Product Name: CriticalStack Intel  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.2\.7532  

This app integrates with the CriticalStack feed to implement investigative actions


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


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a CriticalStack Intel asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**criticalStackServer** |  required  | string | CriticalStack Client Location \(IP/hostname\)
**sshUser** |  required  | string | CriticalStack SSH User
**sshPassword** |  required  | password | CriticalStack SSH Password
**criticalStackPrefix** |  required  | string | CriticalStack List Prefix
**criticalStackApiKey** |  required  | password | CriticalStack API Key
**criticalStackFileLoc** |  required  | string | Critical Stack master\-public\.bro\.dat Location
**verifyPhantomServerCert** |  optional  | boolean | Verify Phantom Server Certificate

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate connectivity to CriticalStack  
[ip reputation](#action-ip-reputation) - Checks IP against CriticalStack IP lists  
[domain reputation](#action-domain-reputation) - Checks domain against CriticalStack domain lists  
[file reputation](#action-file-reputation) - Checks file against CriticalStack file hashes  

## action: 'test connectivity'
Validate connectivity to CriticalStack

Type: **test**  
Read only: **True**

<p><strong>Details\:</strong></p><ul><li>Validates connectivity to the host on which the CriticalStack client is installed\.</li><li>Validates the ability to perform CriticalStack 'list' command on CriticalStack host\.</li><li>Validates connectivity to Phantom API\.</li></ul>

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'ip reputation'
Checks IP against CriticalStack IP lists

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP address to investigate | string |  `ip` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.ip | string |  `ip` 
action\_result\.data\.\*\.ip | string |  `ip` 
action\_result\.data\.\*\.source | string | 
action\_result\.summary\.additional\_details | string | 
action\_result\.summary\.detected\_ip\_count | numeric | 
action\_result\.summary\.list\_prefix | string | 
action\_result\.summary\.lists\_updated | boolean | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'domain reputation'
Checks domain against CriticalStack domain lists

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**domain** |  required  | Domain to investigate | string |  `domain` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.domain | string |  `domain` 
action\_result\.data\.\*\.domain | string |  `domain` 
action\_result\.data\.\*\.source | string | 
action\_result\.summary\.additional\_details | string | 
action\_result\.summary\.detected\_domain\_count | numeric | 
action\_result\.summary\.list\_prefix | string | 
action\_result\.summary\.lists\_updated | boolean | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'file reputation'
Checks file against CriticalStack file hashes

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**hash** |  required  | File hash to investigate | string |  `hash`  `sha256`  `sha1`  `md5` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.hash | string |  `hash`  `sha256`  `sha1`  `md5` 
action\_result\.data\.\*\.hash | string |  `hash`  `sha256`  `sha1`  `md5` 
action\_result\.data\.\*\.source | string | 
action\_result\.summary\.additional\_details | string | 
action\_result\.summary\.detected\_hash\_count | numeric | 
action\_result\.summary\.list\_prefix | string | 
action\_result\.summary\.lists\_updated | boolean | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 