## Setup Dipendenze
È suggerito abilitare un [venv](https://docs.python.org/3/library/venv.html), per isolare le dipendenze del progetto.

Successivamente, le dipendenze sono installabili con `pip install -r requirements.txt`.

## Setup bot
1. Creare nella root del progetto un file `.env`; questo conterrà le informazioni base della configurazione.
2. Aggiungere i due campi essenziali nel file. Esempio: 
    ```
    TELEGRAM_API_KEY=<API KEY DA Bot Father>
    DATABASE_URL=postgresql://unito_bot:password@localhost:5432/unito_bot
    ```

## Setup database
È necessario un database PostgreSQL.
Personalmente suggerisco di usare un container, ma qualunque istanza recente va più che bene!

Per far generare automaticamente le tabelle potete eseguire il comando `alembic upgrade heads`.