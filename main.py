from flask import Flask, render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, EmailField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db' #указываем путь для БД
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False #отключение модификаторов отслеживания БД
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app) #объявление бд

class Note(db.Model): #создание таблицы
    id = db.Column(db.Integer, primary_key=True) #создание полей
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Note Text', validators=[DataRequired()])
    submit = SubmitField('Save')

# ---- Добавление ----
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = NoteForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        note = Note(title=title, content=content) #создание объекта для БД
        db.session.add(note) #добавление эл. в БД
        db.session.commit() #сохранение эл. в БД
        return redirect("/")
    return render_template("add.html", form=form)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        search_request  = request.form.get("search-request")
        notes = Note.query.filter(Note.title.like(f"%{search_request}%")).all()
        return render_template("main.html", notes=notes, search_data=search_request)

    notes = Note.query.all() #считать все данные с БД
    return render_template("main.html", notes=notes,  search_data="")

# ---- Просмотр ----
@app.route('/note/<int:id>',)
def note(id):
    note = Note.query.get(id) #получить информацию по эл базы данных
    return render_template("note.html", note=note)

# ---- Удаление ----
@app.route('/delete-note/<int:id>')
def delete_note(id):
    note = Note.query.get(id) #получить заметку
    db.session.delete(note)  #удалить заметку
    db.session.commit() #сохранить изменения
    return redirect("/") # вернуться на главную

# ---- Изменение ----
@app.route('/edit-note/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    note = Note.query.get(id)
    form = NoteForm(obj=note) #obj=note передать объект в форму
    if form.validate_on_submit(): #условие что данные были отправленны
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        return redirect("/")
    return render_template("update.html", form=form)

if __name__ == '__main__':
    with app.app_context(): #открытие всех файлов приложения
        db.create_all() #создание файла БД
    app.run(debug=True)



