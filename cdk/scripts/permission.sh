
aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::184898280326:role/c3l-engageai-glue-crawler-anl \
  --resource '{ "Database": {"Name": "c3l-engageai-datalake-anl" } }' \
  --permissions "ALL" \
  --region ap-southeast-2 \
  --profile c3l-analytics


aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_Admin_Access_for_all_Accounts_27499b6293fca4d9 \
  --permissions ALL \
  --permissions-with-grant-option ALL \
  --resource '{
      "Table": {
          "DatabaseName": "c3l-engageai-datalake-anl",
          "TableWildcard": {}
      }
  }' \
  --region ap-southeast-2 \
  --profile c3l-analytics

aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_Admin_Access_for_all_Accounts_27499b6293fca4d9 \
  --permissions ALL \
  --permissions-with-grant-option ALL \
  --resource '{
      "Table": {
          "DatabaseName": "engage-ai-dataset",
          "TableWildcard": {}
      }
  }' \
  --region ap-southeast-2 \
  --profile c3l-analytics


aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520 \
  --permissions ALL \
  --permissions-with-grant-option ALL \
  --resource '{
      "Table": {
          "DatabaseName": "engage-ai-dataset",
          "TableWildcard": {}
      }
  }' \
  --region ap-southeast-2 \
  --profile c3l-analytics


# Set up cdk role as lakeformation administrator
aws lakeformation put-data-lake-settings \
  --data-lake-settings '{
    "DataLakeAdmins":[{"DataLakePrincipalIdentifier":"arn:aws:iam::184898280326:role/cdk-hnb659fds-cfn-exec-role-184898280326-ap-southeast-2"}]
  }' \
  --region ap-southeast-2 \
  --profile c3l-analytics