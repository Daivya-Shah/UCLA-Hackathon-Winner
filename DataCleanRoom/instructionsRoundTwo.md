# Multiparty data sharing confidential computing data clean room solution
The following is our process to setting up a data clean room solution for part 1 of the GES hackathon. It is a prototype solution for a Data Clean Room which facilitates the sharing of data between two parties: Advertisers and publishers. These two parties will pass in encrypted data which will be used to generate synthetic data and predictive analytics. The use of a Trusted Execution environment and remote key/attestation server ensures that the data is safe while 'in use'. 

The chosen process follows a 'background check model' of verification where the relying party asks for verification when the attester presents its evidence'. It was chosen because it is the most common in the industry and it is easier to revoke access in case of any issues.

## Set up an Azure confidential VM
Follow the steps indicated in the microsoft documentation to create a confidential VM
https://learn.microsoft.com/en-us/azure/confidential-computing/quick-create-confidential-vm-portal#prerequisites

Note: The exact instance of VM is not so much important as long as it is listed as a 'confidential VM'. Can choose a bigger or smaller size depending on the usecase. It is to note that sizes availible may be limited based on the Zone or Region specified. For this specific implementation it should be running Linux, Ubuntu with a version of 22.04 or above

Below are the specifications used in the demo
- Size: DC4s_v2
- RAM (GiB): 16
- Datadisks: 4
- Max IPOS: 6400
- Local Storage (GiB) = 200(SCSI)
- Premium disk: Supported
- Cost/hr: $0.38

Make sure that when prompted, save the private key in a place that you will remember.

## Install Tools
```
sudo apt-get update
```
```
sudo apt install tpm2-tools -y
```
```
sudo apt install tpm2-pytss -y
```

## Send encrypted resources to VM
Using a remote service such as Azure makes it easy for shareholders to securely upload their data. In this scenario, we are given a .bin file encrypted with AES (Advanced Encryption Standard) to act as shareholder data but in the multiparty scenario, it is possible for each party to access on their own machine using their unique private key. It is also possible to give each user's different permissions based on their private key. This can be utilized for data confidentiality between parties, making sure that neither party can access the other party's data or code. 

### Uploading data via scp
In a multiparty scenario each party can configure their own seperate private key and connect it with the VM. Idealy both parties would use Azure Key Vault for storing their keys as it allows for easy integration with Azure VMs, easy managemnt of access policies as well as industry leading encryption, centralized secret management and hardware security modules.

In this demo due to cost constraints, will be done using a private key saved on a local Windows machine.

After configuring a new VM you can download a private key. To upload a file to the VM from a Windows machine, open Windows PowerShell and enter:
```
scp -i <private-key-path> <file-to-be-uploaded-path> username@public-ip:/desired/destination/path/on/vm
```

Please see https://learn.microsoft.com/en-us/azure/virtual-machines/copy-files-to-vm-using-scp for more details

Afterwards in the terminal for the VM you can use ls in the target directory to check whether the file has been succesfully transfered 

If you don't see your file, you may be logged in as the wrong user. You can use the following to change users:
```
sudo su - <username>
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

### After the following steps you should have these files on the VM
rsa_ak.ctx, rsa_ak.name, rsa_ak.priv, rsa_ak.pub, rsa_ek.ctx, rsa_ek.pub, and your uploaded data, model scripts and decryption script

## Save Attestation public key
Do this for each confidential VM in the system. Store the Attestation Keys into remote key/attestation server for future usage. See below for how to set up a remote key server and how to send the public key to that server

## Generate PCR values
Platform configuration registers are special TPM2 objects of which can only be modified or written to by hash extention mechanism. This property will ensure the integrity of our code 

### Extending values into PCR indices 
In order to ensure the integrity of a client's code. We must first take the hash of the code, then extend it to the PCR

**Hashing data**
Note: change test_model.py with your desired file

Calculate and export the SHA-256 hash:
```
export SHA256_DATA=$(cat test_model.py | openssl dgst -sha256 -binary | xxd -p -c 32)
```

Calculate and export the SHA-1 hash:
```
export SHA1_DATA=$(cat test_model.py | openssl dgst -sha1 -binary | xxd -p -c 20)
```

**Check the hash values**
```
env | grep SHA1
env | grep SHA256
```

**Extending to PCR**
```
sudo tpm2_pcrextend 23:sha1=$SHA1_DATA,sha256=$SHA256_DATA
```

**REPEAT THIS FOR HOWEVER MANY DATA/CODE FILES THAT ARE APART OF THIS CONFIDENTIAL PROCESS**
It is to note that the order of PCRs is important therefore if you mix up the order, you can reset the PCR23 for any mistakes using: 
```
tpm2_pcrreset 23
```

A quote is a signed version of our PCR. It is signed by the attestation key
**Create Quote from PCR23**
```
export SERVICE_PROVIDER_NONCE="12345678"
```
```
tpm2_quote \
--key-context rsa_ak.ctx \
--pcr-list sha1:23+sha256:23 \
--message pcr_quote.plain \
--signature pcr_quote.signature \
--qualification $SERVICE_PROVIDER_NONCE \
--hash-algorithm sha256 \
--pcr pcr.bin
```

## Verify the quote on remote replying party
Now that we have collected all of our evidence, we can send the quote to the remote attestation server to verify it. The reason why we verify the quote on a seperate server is becuase an underlying principle in many confidential computing practices is the "Zero-Trust-Model" which states that no single component within the infastructure is fully trusted. This includes our Trusted Execution Environment. Please see below on how to setup the specified remote replying party.

### Setting up a remote key/attestation
In this case study, we will be using a second Azure Confidential VM as our remote key/attestation server as it provides the same security and managerial benefits as our Trusted Execution Environment. Idealy, the decryption key should be stored securily using a service such as azure key vault, but in this demo it will be stored in a textfile on the remote attestation server (for demo purposes only)

To get started with the remote key/attestation server, follow the same steps at beginning to make a new Azure Confidential VM. Note that the size may be much smaller than the TEE as the tasks of this new server are not computationally expensive.

### Verifying the quote on remote attestation server

**Send quote to attestation server**
Upload pcr_quote.plain and pcr_quote.signature from TEE to remote attestation server
Note: This should be done on a service such as azure storage which will secure the data in storage as well as in transport, a cheaper but less secure and scalable option that we will not explore in this demo is utilizing a VM as a file server role. 

Do the following on the TEE VM
Install azure CLI
```
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```
Configure CLI by logging in 
```
az login

```
Create a storage account and storage container (can also do this step in the azure portal)
```
az storage account create --name mystorageaccount --resource-group myResourceGroup --location eastus --sku Standard_LRS
az storage container create --account-name mystorageaccount --name mycontainer
```
Upload the quote files to Azure Blob Storage
```
az storage blob upload --account-name mystorageaccount --container-name mycontainer --name pcr_quote.plain --file /path/to/pcr_quote.plain
az storage blob download --account-name mystorageaccount --container-name mycontainer --name pcr_quote.signature --file /path/to/destination/pcr_quote.signature
```
Do the following on the remote attestations server VM
Install azure CLI
```
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```
Configure CLI by logging in 
```
az login

```
Download the quote files from Azure Blob Storage
```
az storage blob download --account-name mystorageaccount --container-name mycontainer --name pcr_quote.plain --file /path/to/destination/pcr_quote.plain
az storage blob download --account-name mystorageaccount --container-name mycontainer --name pcr_quote.signature --file /path/to/destination/pcr_quote.signature
```


**Verify Quote**
```
export SERVICE_PROVIDER_NONCE="12345678"

tpm2_checkquote \
--public rsa_ak.pub \
--message pcr_quote.plain \
--signature pcr_quote.signature \
--qualification $SERVICE_PROVIDER_NONCE \
--pcr pcr.bin
```

**If quote is valid, send decryption key to TEE**
Quote is valid if checkquote returns a 0. (Please see https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_checkquote.1.md for more details)

If the quote is valid, we will send the decryption key to TEE. This process can easily be automated through scripts but due to time constraints we will manually check the output of checkquote, and send the decryption wrapper key using azure key services.

Uploading to key vault
```
az keyvault key import --vault-name MyKeyVault --name MyKeyName --pem-file /path/to/mykey.pem
```

## Get Encrypted Wrapper Key via TLS from Key Server into clean room (TEE), Then Decrypt the Model and Data 
```
az keyvault key download --vault-name <your-key-vault-name> --name <your-key-name> --file <path-to-save-key>
```
**Run decrypt.py on data and model using returned key**
Replace the key variable with returned key. Modify code to run the decrypt function on specified files (in this case train.bin)

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
* https://learn.microsoft.com/en-us/azure/virtual-machines/copy-files-to-vm-using-scp
* https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_checkquote.1.md
* https://pypi.org/project/requests/
* https://www.redhat.com/en/blog/introduction-confidential-virtual-machines
* https://learn.microsoft.com/en-us/azure/confidential-computing/virtual-tpms-in-azure-confidential-vm
* https://www.redhat.com/en/blog/attestation-confidential-computing
* https://tpm2-software.github.io/tpm2-tss/getting-started/2019/12/18/Remote-Attestation.html



