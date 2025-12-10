from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Để dùng flash message

# Cấu hình DB (Thay thông tin AWS RDS của bạn vào đây)
db_config = {
    'user': 'admin',
    'password': 'MatKhauCuaBan123',
    'host': 'btl-db.xxxx.us-east-1.rds.amazonaws.com',
    'database': 'ngoaingu_db'
}


def get_db():
    return mysql.connector.connect(**db_config)


@app.route('/')
def index():
    return render_template('layout.html')  # Trang chủ dashboard


# --- CHỨC NĂNG 1: NHẬP ĐIỂM (Tương ứng Sequence 2) ---
# Mô tả: Chọn lớp -> Hiện danh sách học viên -> Nhập điểm -> Lưu
@app.route('/grades', methods=['GET', 'POST'])
def enter_grades():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Logic xử lý khi bấm nút "Lưu điểm"
        student_id = request.form['student_id']
        class_id = request.form['class_id']
        listening = request.form['listening']

        # Kiểm tra xem đã có điểm chưa để Insert hoặc Update
        cursor.execute("SELECT * FROM scores WHERE student_id=%s AND class_id=%s", (student_id, class_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE scores SET listening_score=%s WHERE id=%s
            """, (listening, existing['id']))
        else:
            cursor.execute("""
                INSERT INTO scores (student_id, class_id, listening_score) VALUES (%s, %s, %s)
            """, (student_id, class_id, listening))

        conn.commit()
        flash('Đã cập nhật điểm thành công!', 'success')
        return redirect(url_for('enter_grades'))

    # GET: Hiển thị form nhập điểm
    # Lấy danh sách học viên để chọn
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    # Lấy danh sách lớp
    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    conn.close()
    return render_template('enter_grades.html', students=students, classes=classes)


# --- CHỨC NĂNG 2: TẠO HÓA ĐƠN (Tương ứng Sequence 3) ---
# Mô tả: Chọn học viên -> Chọn khóa học -> Hệ thống tính tiền -> Lưu hóa đơn
@app.route('/invoice', methods=['GET', 'POST'])
def create_invoice():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']

        # Lấy giá tiền từ bảng Course (Logic nghiệp vụ)
        cursor.execute("SELECT tuition_fee FROM courses WHERE id = %s", (course_id,))
        course = cursor.fetchone()
        amount = course['tuition_fee']

        # Lưu vào bảng Invoices
        cursor.execute("INSERT INTO invoices (student_id, course_id, amount, status) VALUES (%s, %s, %s, 'unpaid')",
                       (student_id, course_id, amount))
        conn.commit()
        flash('Đã tạo hóa đơn thu tiền thành công!', 'success')
        return redirect(url_for('create_invoice'))

    # GET: Load dữ liệu cho form
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    conn.close()
    return render_template('create_invoice.html', students=students, courses=courses)


if __name__ == '__main__':
    app.run(debug=True)