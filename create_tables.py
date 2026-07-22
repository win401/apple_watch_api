from database import Base, engine
import models


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL 테이블 생성 완료")