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
    actor = graphene.Field(ActorType, name=graphene.String())
    movie = graphene.Field(MovieType, id=graphene.Int())
    actors = graphene.List(ActorType)
    movies = graphene.List(MovieType)

    def resolve_actor(self, info, **kwargs):
        """
            In the resolve_actor function we retrieve the ID from the query parameters and 
            return the actor from our database with that ID as its primary key
        """
        name = kwargs.get('name')

        if id is not None:
            return Actor.objects.get(name__icontains=name)

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


# Mutation Add/Edit


class ActorInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()


class MovieInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    actors = graphene.List(ActorInput)
    year = graphene.Int()


# Create mutations for actors
class CreateActor(graphene.Mutation):

    class Arguments:
        inputdata = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, inputdata=None):
        ok = True
        actor_instance = Actor(name=inputdata.name)
        actor_instance.save()
        return CreateActor(ok=ok, actor=actor_instance)


class UpdateActor(graphene.Mutation):

    class Arguments:
        id = graphene.Int(required=True)
        inputdata = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, id, inputdata=None):
        ok = False
        actor_instance = Actor.objects.get(pk=id)
        if actor_instance:
            ok = True
            actor_instance.name = inputdata.name
            actor_instance.save()
            return UpdateActor(ok=ok, actor=actor_instance)
        return UpdateActor(ok=ok, actor=None)

class Mutation(graphene.ObjectType):

    create_actor = CreateActor.Field()
    update_actor = UpdateActor.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


