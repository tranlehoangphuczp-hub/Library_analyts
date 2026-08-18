from sqlalchemy import create_engine, text
from config import TARGET

engine = create_engine(
    f"postgresql+psycopg2://{TARGET['username']}:{TARGET['password']}@"
    f"{TARGET['host']}:{TARGET['port']}/{TARGET['database']}"
)

print("=" * 60)
print("XÂY DỰNG FACT_BORROW (TỐI ƯU PURE SQL & AN TOÀN DATA)")
print("=" * 60)

sql = """
-- 1. Tạo bảng Fact
CREATE TABLE IF NOT EXISTS library_dw.fact_borrow (
    fact_key INT PRIMARY KEY,
    borrow_ticket_id INT,
    borrow_book_id INT,
    user_key INT,
    role_key INT,
    school_key INT,
    book_key INT,
    subject_key INT,
    borrow_date_key INT,
    return_date_key INT,
    book_count INT,
    is_returned BOOLEAN,
    
    CONSTRAINT fk_fact_user
    FOREIGN KEY (user_key)
    REFERENCES library_dw.dim_user(user_key),

    CONSTRAINT fk_fact_role
    FOREIGN KEY (role_key)
    REFERENCES library_dw.dim_role(role_key),

    CONSTRAINT fk_fact_school
    FOREIGN KEY (school_key)
    REFERENCES library_dw.dim_school(school_key),

    CONSTRAINT fk_fact_book
    FOREIGN KEY (book_key)
    REFERENCES library_dw.dim_book(book_key),

    CONSTRAINT fk_fact_subject
    FOREIGN KEY (subject_key)
    REFERENCES library_dw.dim_subject(subject_key),

    CONSTRAINT fk_fact_borrow_date
    FOREIGN KEY (borrow_date_key)
    REFERENCES library_dw.dim_date(date_key),

    CONSTRAINT fk_fact_return_date
    FOREIGN KEY (return_date_key)
    REFERENCES library_dw.dim_date(date_key)

);

-- 2. Index
CREATE INDEX IF NOT EXISTS idx_fact_user
ON library_dw.fact_borrow(user_key);
    
CREATE INDEX IF NOT EXISTS idx_fact_role
ON library_dw.fact_borrow(role_key);

CREATE INDEX IF NOT EXISTS idx_fact_school
ON library_dw.fact_borrow(school_key);

CREATE INDEX IF NOT EXISTS idx_fact_book
ON library_dw.fact_borrow(book_key);

CREATE INDEX IF NOT EXISTS idx_fact_subject
ON library_dw.fact_borrow(subject_key);

CREATE INDEX IF NOT EXISTS idx_fact_borrow_date
ON library_dw.fact_borrow(borrow_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_return_date
ON library_dw.fact_borrow(return_date_key);

-- 3. Xóa dữ liệu cũ
TRUNCATE TABLE library_dw.fact_borrow CASCADE;

-- 4. Nạp dữ liệu
INSERT INTO library_dw.fact_borrow (
    fact_key,
    borrow_ticket_id,
    borrow_book_id,
    user_key,
    role_key,
    school_key,
    book_key,
    subject_key,
    borrow_date_key,
    return_date_key,
    book_count,
    is_returned
)

WITH raw_fact AS (

    SELECT DISTINCT

        bt.id AS borrow_ticket_id,
        bb.id AS borrow_book_id,
        COALESCE(du.user_key,0) AS user_key,
        COALESCE(du.role_key,0) AS role_key,
        COALESCE(du.school_key,0) AS school_key,
        COALESCE(db.book_key,0) AS book_key,
        COALESCE(db.subject_key,0) AS subject_key,
        COALESCE(d1.date_key,0) AS borrow_date_key,
        COALESCE(d2.date_key,0) AS return_date_key, 1 AS book_count,
        CASE
            WHEN bt.actual_return_date IS NULL THEN FALSE
            ELSE TRUE
        END AS is_returned
        
    FROM clean_data.library_borrow_ticket bt

    INNER JOIN clean_data.library_borrow_book bb
        ON bt.id = bb.borrow_ticket_id

    INNER JOIN clean_data.library_dang_ki_ca_biet dk
        ON bb.dang_ki_ca_biet_id = dk.id

    LEFT JOIN clean_data.library_book_copy bc
        ON dk.book_copy_id = bc.id

    LEFT JOIN clean_data.library_book b
        ON bc.book_id = b.id

    LEFT JOIN library_dw.dim_book db
        ON b.id = db.book_id

    LEFT JOIN library_dw.dim_user du
        ON bt.user_id = du.user_id

    LEFT JOIN library_dw.dim_date d1
        ON DATE(bt.actual_borrow_date) = d1.full_date

    LEFT JOIN library_dw.dim_date d2
        ON DATE(bt.actual_return_date) = d2.full_date

    WHERE bt.actual_borrow_date >= CURRENT_DATE - INTERVAL '1 year'

)

SELECT

    ROW_NUMBER() OVER (
    ORDER BY borrow_ticket_id, borrow_book_id) AS fact_key,
    borrow_ticket_id,
    borrow_book_id,
    user_key,
    role_key,
    school_key,
    book_key,
    subject_key,
    borrow_date_key,
    return_date_key,
    book_count,
    is_returned

FROM raw_fact;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("=" * 60)
print("✅ ĐÃ XÂY DỰNG FACT_BORROW THÀNH CÔNG VÀ AN TOÀN")
print("=" * 60)