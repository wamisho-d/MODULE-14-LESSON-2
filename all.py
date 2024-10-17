# Task 1: Define GraphQL Schema 
# schema.py
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define the product model
class ProductModel(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)

# GraphQL Object Type based on ProductModel
class Product(SQLAlchemyObjectType):
    class Meta:
        model = ProductModel

# Input types for mutations
class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    quantity = graphene.Int(required=True)
    category = graphene.String(required=True)

# Queries for fetching products
class Query(graphene.ObjectType):
    products = graphene.List(Product)

    def resolve_products(self, info):
        return ProductModel.query.all()

# Mutation to create a product
class CreateProduct(graphene.Mutation):
    class Arguments:
        product_data = ProductInput(required=True)
    
    product = graphene.Field(lambda: Product)
 
    def mutate(self, info, product_data):
        product = ProductModel(
            name=product_data.name,
            price=product_data.price,
            quantity=product_data.quantity,
            category=product_data.category
        )

        db.session.add(product)
        db.session.commit()
        return CreateProduct(product=product)
# Mutation to update a product
class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        product_data = ProductInput(required=True)
    
    product = graphene.Field(lambda: Product)

    def mutate(self, info, id, product_data):
        product = ProductModel.query.get(id)
        if product:
            product.name = product_data.name
            product.price = product_data.price
            product.quantity = product_data.quantity
            product.category = product_data.category
            db.session.commit()
        return UpdateProduct(product=product)

# Mutation to delete a product
class DeleteProduct(graphene.Muatation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        product = ProductModel.query.get(id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return DeleteProduct(ok=True)
        return DeleteProduct(ok=False)

# Root Mutation for Create, Update, and Delete operation
class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

# Final schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Task 2: Flask Server Setup
# app.py
from falsk import Flask
from flask_graphql import GraphQLView
from schema import schema, db

app = Flask(__name__)

# Configure SQLite database for simplicity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bakery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()

# Define the GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # Enable the GraphiQL interface
    )
)

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)


