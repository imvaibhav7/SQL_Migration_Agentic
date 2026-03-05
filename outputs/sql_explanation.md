The provided SQL migration scripts are designed to transfer data from source tables into target tables within a database. Each script follows a similar structure, focusing on inserting data into specific target tables while transforming and mapping fields from the source tables. Below is a detailed explanation of each migration SQL statement:

1. **Contact Table Migration**:
   ```sql
   INSERT INTO Contact (Id, FirstName, LastName, Email, Phone, Type, CreatedDate)
   SELECT CAST(constituent_id AS TEXT) AS Id,
          first_name AS FirstName,
          last_name AS LastName,
          LOWER(email_address) AS Email,
          phone_number AS Phone,
          constituent_type AS Type,
          created_date AS CreatedDate
   FROM re_constituents AS src;
   ```
   - **Target Table**: `Contact`
   - **Purpose**: This statement inserts records into the `Contact` table.
   - **Field Mapping**:
     - `constituent_id` is cast to text and mapped to `Id`.
     - `first_name` and `last_name` are directly mapped to `FirstName` and `LastName`.
     - `email_address` is converted to lowercase for consistency in the `Email` field.
     - `phone_number`, `constituent_type`, and `created_date` are directly mapped to their respective fields.
   - **Source Table**: `re_constituents`

2. **Donation Table Migration**:
   ```sql
   INSERT INTO Donation (Id, ContactId, CampaignId, Amount, DonationDate, PaymentMethod, Description)
   SELECT CAST(gift_id AS TEXT) AS Id,
          CAST(constituent_id AS TEXT) AS ContactId,
          CAST(campaign_id AS TEXT) AS CampaignId,
          gift_amount AS Amount,
          gift_date AS DonationDate,
          payment_method AS PaymentMethod,
          TRIM(notes) AS Description
   FROM re_gifts AS src;
   ```
   - **Target Table**: `Donation`
   - **Purpose**: This statement inserts records into the `Donation` table.
   - **Field Mapping**:
     - `gift_id` is cast to text and mapped to `Id`.
     - `constituent_id` and `campaign_id` are also cast to text and mapped to `ContactId` and `CampaignId`, respectively.
     - `gift_amount`, `gift_date`, and `payment_method` are directly mapped to their respective fields.
     - `notes` is trimmed of whitespace and mapped to `Description`.
   - **Source Table**: `re_gifts`

3. **Campaign Table Migration**:
   ```sql
   INSERT INTO Campaign (Id, Name, TargetAmount, StartDate, EndDate, Status)
   SELECT CAST(campaign_id AS TEXT) AS Id,
          campaign_name AS Name,
          goal_amount AS TargetAmount,
          start_date AS StartDate,
          end_date AS EndDate,
          UPPER(status) AS Status
   FROM re_campaigns AS src;
   ```
   - **Target Table**: `Campaign`
   - **Purpose**: This statement inserts records into the `Campaign` table.
   - **Field Mapping**:
     - `campaign_id` is cast to text and mapped to `Id`.
     - `campaign_name`, `goal_amount`, `start_date`, and `end_date` are directly mapped to their respective fields.
     - `status` is converted to uppercase for standardization in the `Status` field.
   - **Source Table**: `re_campaigns`

4. **Address Table Migration**:
   ```sql
   INSERT INTO Address (Id, ContactId, Street, City, State, PostalCode, Country)
   SELECT CAST(address_id AS TEXT) AS Id,
          CAST(constituent_id AS TEXT) AS ContactId,
          street_line1 AS Street,
          city AS City,
          state_province AS State,
          postal_code AS PostalCode,
          country AS Country
   FROM re_addresses AS src;
   ```
   - **Target Table**: `Address`
   - **Purpose**: This statement inserts records into the `Address` table.
   - **Field Mapping**:
     - `address_id` is cast to text and mapped to `Id`.
     - `constituent_id` is cast to text and mapped to `ContactId`.
     - `street_line1`, `city`, `state_province`, `postal_code`, and `country` are directly mapped to their respective fields.
   - **Source Table**: `re_addresses`

### Summary
Each SQL statement is structured to ensure that data is accurately transferred from the source tables to the target tables, with appropriate data type conversions and transformations applied where necessary. The use of `CAST` ensures that identifiers are in the correct format, while functions like `LOWER` and `TRIM` help maintain data consistency and cleanliness.