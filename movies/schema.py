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


class CreateMovie(graphene.Mutation):

    class Arguments:
        inputdata = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, inputdata=None):
        ok, actors = True, []
        for actor_input in inputdata.actors:
            actor_obj = Actor.objects.get(pk=actor_input.id)
            if actor_obj is None:
                return CreateMovie(ok=False, movie=None)
            actors.append(actor_obj)
        movie_instance = Movie(
                title=inputdata.title,
                year=inputdata.year
            )
        movie_instance.save()
        movie_instance.actors.set(actors)
        movie_instance.save()
        return CreateMovie(ok=ok, movie=movie_instance)


class UpdateMovie(graphene.Mutation):

    class Arguments:
        id = graphene.Int(required=True)
        inputdata = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, id, inputdata=None):
        ok = False
        movie_instance = Movie.objects.get(pk=id)
        if movie_instance:
            ok, actors = True, []
            for actor_input in inputdata.actors:
                actor = Actor.objects.get(pk=actor_input.id)
                if actor is None:
                    return CreateMovie(ok=False, movie=None)
                actors.append(actor)
            movie_instance.title = inputdata.title
            movie_instance.year = inputdata.year
            movie_instance.actors.set(actors)
            movie_instance.save()
            return UpdateMovie(ok=ok, movie=movie_instance)
        return UpdateMovie(ok=ok, movie=None)


class Mutation(graphene.ObjectType):

    create_actor = CreateActor.Field()
    update_actor = UpdateActor.Field()
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


"""
The other way of registration is

import graphene
import dj_graphql_exmaple.movies.schema

class Query(dj_graphql_exmaple.movies.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

class Mutation(dj_graphql_exmaple.movies.schema.Mutation, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
"""
