# HashiCorp Vault — Local Dev Lab

Hands-on exploration of HashiCorp Vault running in dev mode on Fedora Linux.

## What This Covers
- Running Vault server in dev mode
- KV (Key-Value) secrets engine
- AppRole authentication method
- Policy-based access control

## Setup

### Install Vault (Fedora)
```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager addrepo --from-repofile=https://rpm.releases.hashicorp.com/fedora/hashicorp.repo
sudo dnf install vault -y
vault --version
```

### Start Dev Server
```bash
vault server -dev
```

### Configure Shell
```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='<root-token-from-dev-server>'
vault status
```

## KV Secrets

```bash
# Write
vault kv put secret/myapp password=s3cr3t db_host=localhost

# Read
vault kv get secret/myapp

# Read specific field
vault kv get -field=password secret/myapp
```

### Output

== Secret Path ==
secret/data/myapp

======= Metadata =======
Key                Value
---                -----
created_time       2026-04-25T15:54:34.327744793Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

====== Data ======
Key         Value
---         -----
db_host     localhost
password    s3cr3t

mukeshk@fedora:~$ vault kv get -field=password secret/myapp
s3cr3t

## AppRole Authentication

AppRole is designed for machine-to-machine auth. An app gets a Role ID + Secret ID and exchanges them for a short-lived token.

```bash
# Enable AppRole
vault auth enable approle

# Create policy
vault policy write myapp-policy - <<EOF
path "secret/data/myapp" {
  capabilities = ["read"]
}
EOF

# Create role
vault write auth/approle/role/myapp \
    token_policies="myapp-policy" \
    token_ttl=1h \
    token_max_ttl=4h

# Fetch credentials
vault read auth/approle/role/myapp/role-id
vault write -force auth/approle/role/myapp/secret-id

# Login as app
vault write auth/approle/login \
    role_id="<e44ac1de-685e-0f15-4d32-de05c64c83eb>" \
    secret_id="<REDACTED>"
```

## Key Concepts Learned

| Concept | Description |
|---------|-------------|
| Dev Mode | In-memory, auto-unsealed, single-node — for learning only |
| KV v2 | Versioned key-value secrets engine |
| AppRole | Auth method for services/apps, not humans |
| Policy | HCL rules defining what paths a token can access |
| Token TTL | Tokens expire — forces credential rotation |

## References
- [Vault Dev Mode](https://developer.hashicorp.com/vault/docs/concepts/dev-server)
- [KV Secrets Engine](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2)
- [AppRole Auth](https://developer.hashicorp.com/vault/tutorials/auth-methods/approle)
