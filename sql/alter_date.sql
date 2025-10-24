BEGIN;
DO $$
DECLARE coltype text;
BEGIN
    SELECT data_type INTO coltype
    FROM information_schema.columns
    WHERE table_schema='public' AND table_name='expenses' AND column_name='date';
    IF coltype <> 'date' THEN
        ALTER TABLE public.expenses
            ALTER COLUMN "date" TYPE DATE
            USING to_date("date", 'DD.MM.YYYY');
    END IF;
END $$;
COMMIT;
