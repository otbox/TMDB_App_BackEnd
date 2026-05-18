from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Rating

ratings_bp = Blueprint("ratings", __name__)

@ratings_bp.get("/ratings")
@jwt_required()
def get_ratings():
    user_id = int(get_jwt_identity())

    ratings = Rating.query.filter_by(user_id=user_id).order_by(Rating.updated_at.desc()).all()

    return jsonify([rating.to_dict() for rating in ratings]), 200


@ratings_bp.get("/ratings/<int:movie_id>")
@jwt_required()
def get_rating(movie_id):
    user_id = int(get_jwt_identity())

    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    return jsonify(rating.to_dict()), 200


@ratings_bp.post("/ratings")
@jwt_required()
def create_rating():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON body"}), 400

    movie_id = data.get("movie_id")
    rating_value = data.get("rating")

    if movie_id is None or rating_value is None:
        return jsonify({"message": "movie_id and rating are required"}), 400

    if not isinstance(rating_value, (int, float)):
        return jsonify({"message": "rating must be a number"}), 400

    if rating_value < 0.5 or rating_value > 5:
        return jsonify({"message": "rating must be between 0.5 and 5"}), 400

    existing_rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing_rating:
        return jsonify({"message": "Rating already exists for this movie"}), 409

    rating = Rating(
        user_id=user_id,
        movie_id=movie_id,
        rating=float(rating_value)
    )

    db.session.add(rating)
    db.session.commit()

    return jsonify(rating.to_dict()), 201


@ratings_bp.put("/ratings/<int:movie_id>")
@jwt_required()
def update_rating(movie_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON body"}), 400

    rating_value = data.get("rating")

    if rating_value is None:
        return jsonify({"message": "rating is required"}), 400

    if not isinstance(rating_value, (int, float)):
        return jsonify({"message": "rating must be a number"}), 400

    if rating_value < 0.5 or rating_value > 5:
        return jsonify({"message": "rating must be between 0.5 and 5"}), 400

    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    rating.rating = float(rating_value)
    db.session.commit()

    return jsonify(rating.to_dict()), 200


@ratings_bp.delete("/ratings/<int:movie_id>")
@jwt_required()
def delete_rating(movie_id):
    user_id = int(get_jwt_identity())

    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    db.session.delete(rating)
    db.session.commit()

    return jsonify({"message": "Rating deleted successfully"}), 200