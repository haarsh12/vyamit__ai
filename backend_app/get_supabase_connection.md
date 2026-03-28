# Get Supabase Database Connection String

## Steps to Get Your PostgreSQL Connection String:

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your project**: `lhafpdiovrxxvxyqemtg`
3. **Go to Settings** → **Database**
4. **Find "Connection string"** section
5. **Copy the "URI" format** (it should look like this):

```
postgresql://postgres:[YOUR-PASSWORD]@db.lhafpdiovrxxvxyqemtg.supabase.co:5432/postgres
```

## What to do:

1. **Replace `[YOUR-PASSWORD]`** with your actual database password
2. **Update your `.env` file** with this connection string
3. **Run the table creation script** in Supabase SQL Editor

## Example:
If your password is `mypassword123`, your connection string would be:
```
postgresql://postgres:mypassword123@db.lhafpdiovrxxvxyqemtg.supabase.co:5432/postgres
```

## Security Note:
- Never commit your actual database password to version control
- Use environment variables for production deployments