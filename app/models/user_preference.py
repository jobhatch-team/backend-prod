# from .db import db, environment, SCHEMA, add_prefix_for_prod

# class UserPreference(db.Model):
#     __tablename__ = 'user_preferences'

#     if environment == "production":
#         __table_args__ = {'schema': SCHEMA}

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), unique=True, nullable=False)

#     job_search_status = db.Column(db.String)
#     needs_sponsorship = db.Column(db.Boolean)
#     has_work_authorization = db.Column(db.Boolean)
#     job_types = db.Column(db.String)
#     preferred_locations = db.Column(db.Text)
#     open_to_remote = db.Column(db.Boolean)
#     salary_min = db.Column(db.Integer)
#     salary_max = db.Column(db.Integer)
#     company_size_1_10 = db.Column(db.String)
#     company_size_11_50 = db.Column(db.String)
#     company_size_51_200 = db.Column(db.String)
#     company_size_201_500 = db.Column(db.String)
#     company_size_500_plus = db.Column(db.String)

#     created_at = db.Column(db.DateTime, server_default=db.func.now())

#     user = db.relationship("User", back_populates="user_preference")

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "job_search_status": self.job_search_status,
#             "needs_sponsorship": self.needs_sponsorship,
#             "has_work_authorization": self.has_work_authorization,
#             "job_types": self.job_types,
#             "preferred_locations": self.preferred_locations,
#             "open_to_remote": self.open_to_remote,
#             "salary_min": self.salary_min,
#             "salary_max": self.salary_max,
#             "company_size_1_10": self.company_size_1_10,
#             "company_size_11_50": self.company_size_11_50,
#             "company_size_51_200": self.company_size_51_200,
#             "company_size_201_500": self.company_size_201_500,
#             "company_size_500_plus": self.company_size_500_plus,
#             "created_at": self.created_at.isoformat() if self.created_at else None,
#         }

from .db import db, environment, SCHEMA, add_prefix_for_prod

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), unique=True, nullable=False)

    job_search_status = db.Column(db.String)
    needs_sponsorship = db.Column(db.Boolean)
    has_work_authorization = db.Column(db.Boolean)
    job_types = db.Column(db.String)
    preferred_locations = db.Column(db.Text)
    open_to_remote = db.Column(db.Boolean)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    company_size_1_10 = db.Column(db.String)
    company_size_11_50 = db.Column(db.String)
    company_size_51_200 = db.Column(db.String)
    company_size_201_500 = db.Column(db.String)
    company_size_500_plus = db.Column(db.String)
    
    # Onboarding specific fields
    willing_to_mentor = db.Column(db.Boolean, default=False)
    founder_interests = db.Column(db.String)  # comma-separated: recruiting,fundraising
    investor_interests = db.Column(db.String)  # comma-separated: find_startups,join_program

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", back_populates="user_preference")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_search_status": self.job_search_status,
            "needs_sponsorship": self.needs_sponsorship,
            "has_work_authorization": self.has_work_authorization,
            "job_types": self.job_types,
            "preferred_locations": self.preferred_locations,
            "open_to_remote": self.open_to_remote,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "company_size_1_10": self.company_size_1_10,
            "company_size_11_50": self.company_size_11_50,
            "company_size_51_200": self.company_size_51_200,
            "company_size_201_500": self.company_size_201_500,
            "company_size_500_plus": self.company_size_500_plus,
            "willing_to_mentor": self.willing_to_mentor,
            "founder_interests": self.founder_interests,
            "investor_interests": self.investor_interests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }