from sqlalchemy import create_engine
from config import SOURCE, TARGET


def test_connection(config, name):
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{config['username']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}"
        )

        with engine.connect() as conn:
            print(f"✅ Kết nối {name} thành công!")

    except Exception as e:
        print(f"❌ Kết nối {name} thất bại")
        print(e)


test_connection(SOURCE, "k12production")
test_connection(TARGET, "PostgreSQL Local")