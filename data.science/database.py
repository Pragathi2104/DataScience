"""Persistence boundary with an in-memory fallback for local demonstrations."""

_analyses = []


def save_analysis(analysis):
    _analyses.insert(0, analysis)
    return analysis


def get_analyses():
    return list(_analyses)