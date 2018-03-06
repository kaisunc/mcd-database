from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired

from ..models import Project, Status

class AddProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Project Name"})
    status_id = SelectField('Status', validators=[DataRequired()], id="status_id", coerce=int)
    submit = SubmitField('Add')
    
    # check the db if name is unique
    def validate_name(self, field):
        if Project.query.filter_by(name=field.data).first():
            raise ValidationError('Project Name exists!')

class AddStatusForm(FlaskForm)    :
    name = StringField('Status', validators=[DataRequired()], render_kw={"placeholder": "Status"})
    submit =SubmitField('Add')
    
    def validate_name(self, field):
        if Status.query.filter_by(name=field.data).first():
            raise ValidationError('Status Name exists!')    



