from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import EpisodeRating

episode_ratings_bp = Blueprint("episode_ratings", __name__)


@episode_ratings_bp.get("/episode-ratings")
@jwt_required()
def get_episode_ratings():
    user_id = int(get_jwt_identity())
    ratings = EpisodeRating.query.filter_by(user_id=user_id).order_by(EpisodeRating.updated_at.desc()).all()
    return jsonify([r.to_dict() for r in ratings]), 200


@episode_ratings_bp.get("/episode-ratings/<int:episode_id>")
@jwt_required()
def get_episode_rating(episode_id):
    user_id = int(get_jwt_identity())
    rating = EpisodeRating.query.filter_by(user_id=user_id, episode_id=episode_id).first()
    if not rating:
        return jsonify({"message": "Rating not found"}), 404
    return jsonify(rating.to_dict()), 200


@episode_ratings_bp.post("/episode-ratings")
@jwt_required()
def create_episode_rating():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON body"}), 400

    episode_id = data.get("episode_id")
    rating_value = data.get("rating")

    if episode_id is None or rating_value is None:
        return jsonify({"message": "episode_id and rating are required"}), 400

    if not isinstance(rating_value, (int, float)):
        return jsonify({"message": "rating must be a number"}), 400

    if rating_value < 0.5 or rating_value > 5:
        return jsonify({"message": "rating must be between 0.5 and 5"}), 400

    existing = EpisodeRating.query.filter_by(user_id=user_id, episode_id=episode_id).first()
    if existing:
        return jsonify({"message": "Rating already exists for this episode"}), 409

    rating = EpisodeRating(user_id=user_id, episode_id=episode_id, rating=float(rating_value))
    db.session.add(rating)
    db.session.commit()
    return jsonify(rating.to_dict()), 201


@episode_ratings_bp.put("/episode-ratings/<int:episode_id>")
@jwt_required()
def update_episode_rating(episode_id):
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

    rating = EpisodeRating.query.filter_by(user_id=user_id, episode_id=episode_id).first()
    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    rating.rating = float(rating_value)
    db.session.commit()
    return jsonify(rating.to_dict()), 200


@episode_ratings_bp.delete("/episode-ratings/<int:episode_id>")
@jwt_required()
def delete_episode_rating(episode_id):
    user_id = int(get_jwt_identity())
    rating = EpisodeRating.query.filter_by(user_id=user_id, episode_id=episode_id).first()
    if not rating:
        return jsonify({"message": "Rating not found"}), 404
    db.session.delete(rating)
    db.session.commit()
    return jsonify({"message": "Rating deleted"}), 200
