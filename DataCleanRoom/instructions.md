# Multiparty data sharing confidential computing data clean room solution
The following is our process to setting up a data clean room solution for part 1 of the GES hackathon.

The chosen process follows a 'background check model' of verification where the relying party asks for verification when the attester presents its evidence'. It was chosen because it is the most common in the industry and it is easier to revoke access in case of any issues.

## Set up an Azure confidential VM
Note: The exact instance of VM is not so much important as long as it is listed as a 'confidential VM'. Can choose a bigger or smaller size depending on the usecase. For this specific implementation it should be running Linux, Ubuntu with a version of 22.04 or above
- Size: DC4s_v2
- RAM (GiB): 16
- Datadisks: 4
- Max IPOS: 6400
- Local Storage (GiB) = 200(SCSI)
- Premium disk: Supported
- Cost/hr: $0.38

## Install Tools
```
sudo apt install tpm2-tools -y
```
```
sudo apt install tpm2-pytss -y
```
## Initialize verification keys 

### Create Endorsement Key
The endorsement key is sued to prove that the user is talking to a real TPM.
```
tpm2_createek --ek-context rsa_ek.ctx --key-algorithm rsa --public rsa_ek.pub
```

### Create Attestation Key
Used for signing of evidence (quote and attestation) and derived from the endorsement key 
```
tpm2_createak \
   --ek-context rsa_ek.ctx \
   --ak-context rsa_ak.ctx \
   --key-algorithm rsa \
   --hash-algorithm sha256 \
   --signing-algorithm rsassa \
   --public rsa_ak.pub \
   --private rsa_ak.priv \
   --ak-name rsa_ak.name
```

## Save Attestation public key
Do this for each confidential VM in the system. Store the Attestation Keys into remote key/attestation server for future usage. See below for how to set up a remote key server and how to send secrets to the server

## Generate PCR values
Platform configuration registers are special TPM2 objects of which can only be modified or written to by hash extention mechanism. This property will ensure the integrity of our code 

### Initialize PCR
```
tpm2_pcrread sha1:0,1,2+sha256:0,1,2
```

### Upload data and model to TEE (Both are encrypted)

### Extending values into PCR indices 
In order to ensure the integrity of a client's code. We must first take the hash of the code, then extend it to the PCR

**Hashing data**
*Replace CRITICAL-DATA with your desired data and code*
```
SHA256_DATA=`echo "CRITICAL-DATA" | openssl dgst -sha256 -binary | xxd -p -c 32`
SHA1_DATA=`echo "CRITICAL-DATA" | openssl dgst -sha1 -binary | xxd -p -c 20`
```
**Extending to PCR**
```
tpm2_pcrextend 0:sha1=$SHA1_DATA,sha256=$SHA256_DATA
tpm2_pcrextend 1:sha1=$SHA1_DATA,sha256=$SHA256_DATA
tpm2_pcrextend 2:sha1=$SHA1_DATA,sha256=$SHA256_DATA
```

**Read the PCR values**
```
tpm2_pcrread sha1:0,1,2+sha256:0,1,2
```

### Golden/Reference PCR
This term refers to the summary of the entire 'good state' of the software and data. We must define this good state ourselves. There are multiple ways to calculate the golden PCR state but we will be choosing to do so by using the tpm2_quote tool. It is to note that creating the quote should be done in a trusted execution environment such as in our confidential VM. 

**Create Quote from PCR23 and Generate Golden PCR**
```
tpm2_quote \
--key-context rsa_ak.ctx \
--pcr-list sha1:0,1,2+sha256:0,1,2 \
--message pcr_quote.plain \
--signature pcr_quote.signature \
--qualification SERVICE_PROVIDER_NONCE \
--hash-algorithm sha256 \
--pcr pcr.bin

GOLDEN_PCR=`cat pcr.bin | openssl dgst -sha256 -binary | xxd -p -c 32`
```
### Evaluate PCR values
Now that we have calculated the 'good state' PCR, we can use the golden PCR to evaluate our PCR value.

## Verify the quote
```
export SERVICE_PROVIDER_NONCE="12345678"

tpm2_checkquote \
--public rsa_ak.pub \
--message pcr_quote.plain \
--signature pcr_quote.signature \
--qualification $SERVICE_PROVIDER_NONCE \
--pcr pcr.bin
```

## Setting up a remote key/secret server
We need a remote key/secret server in order to verify the authenticity and integrity of our system. This verification is done with the TPM quote, PCR values and a nonce. In this implementation it makes sense to use an Azure Key Vault for our implementation of the server.

1. Login to azure portal, then nagivate to create resource, Key Vault
2. Fill out fields as desired. Ensure Azure Virtual Machines can access secrets. Then click Review + Create
3. Alternatively, you can use the command line to create an azure key vault
```
az keyvault create --name <your-key-vault-name> --resource-group <your-resource-group> --location <your-location>
```

### NOTE: In terms of a multi-party data sharing scenario, it is important that a policy is properly defined. This can be done through the key vault portal or though the amazon CLI. Permissions can be set to only permit a certain party to access certain data

## Send Evidence to Remote Key/Secret Server
The key vault can be accessed using Azure SDKs, CLI or REST API

1. Install Azure CLI
```
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```
2. Login to azure CLI
```
az login
```
3. Import existing AK to Key Vault
```
az keyvault key import --vault-name <your-key-vault-name> --name <your-key-name> --pem-file mykey.pem
```
For Example
```
az keyvault key import --vault-name myKeyVault --name myImportedKey --pem-file myKey.pem
```

## Get Encrypted Wrapper Key via TLS from Key Server into clean room (TEE), Then Decrypt the Model and Data 
```
az keyvault key download --vault-name <your-key-vault-name> --name <your-key-name> --file <path-to-save-key>
```
**Run decrypt.py on data and model using returned key**
Replace the key variable with returned key. Modify code to run the decrypt function on specified files

## Manipulation of Data 
*The training of the model and creation of synthetic data are found in the second part of the submition*

## Encrypt Output Data Leaving Clean room
Modify code to run the encrypt function on specified files
Return files to permitted users 
Users are returned model insights and synthetic data 


## Sources
* https://tpm2-software.github.io/2020/06/12/Remote-Attestation-With-tpm2-tools.html#what-is-a-pcr-and-how-are-pcr-values-generated
* https://gist.github.com/kenplusplus/f025d04047bc044e139d105b4c708d78
* https://learn.microsoft.com/en-us/azure/confidential-computing/quick-create-confidential-vm-portal#prerequisites
