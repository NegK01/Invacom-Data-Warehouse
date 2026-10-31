CREATE LOGIN mage_user WITH PASSWORD = 'admin1234';
GO
USE staging_invacom;
GO
CREATE USER mage_user FOR LOGIN mage_user;
ALTER ROLE db_owner ADD MEMBER mage_user;
GO