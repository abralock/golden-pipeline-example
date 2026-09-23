resource "azurerm_storage_account" "logs" {
  # Exceptions are inline, with a reason, so they show up in code review and audits.
  #checkov:skip=CKV2_AZURE_1:Log data classified Internal; Microsoft-managed keys approved (SEC-EX-2291)
  #checkov:skip=CKV2_AZURE_33:Private endpoint is created in the network module (terraform/network)
  #checkov:skip=CKV_AZURE_33:Queue service not used by this account
  name                            = "stcorplogs001"
  resource_group_name             = "rg-logs"
  location                        = "southeastasia"
  account_tier                    = "Standard"
  account_replication_type        = "GRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = false
  shared_access_key_enabled       = false

  blob_properties {
    delete_retention_policy {
      days = 14
    }
  }

  sas_policy {
    expiration_period = "01.00:00:00"
  }
}
