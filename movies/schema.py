import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from .models import Actor, Movie


# Create a GraphQL type for the actor model
class ActorType(DjangoObjectType):
    class Meta:
        model = Actor
        interfaces = (graphene.Node, )


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie
        interfaces = (graphene.Node, )


# Create a Query type
class Query(ObjectType):
    """
        The four methods we created in the Query class are called resolvers.
        Resolvers connect the queries in the schema to actual actions done by the database.
        As is standard in Django, we interact with our database via models.
    """
    actor = graphene.Field(ActorType, id=graphene.Int())
    movie = graphene.Field(MovieType, id=graphene.Int())
    actors = graphene.List(ActorType)
    movies = graphene.List(MovieType)

    def resolve_actor(self, info, **kwargs):
        """
            In the resolve_actor function we retrieve the ID from the query parameters and 
            return the actor from our database with that ID as its primary key
        """
        id = kwargs.get('id')

        if id is not None:
            return Actor.objects.get(pk=id)

        return None

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Movie.objects.get(pk=id)

        return None

    def resolve_actors(self, info, **kwargs):
        """
            In the resolve_actors function simply gets all the actors in the database and
            returns them as a list.
        """
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
        return Movie.objects.all()


schema = graphene.Schema(query=Query)