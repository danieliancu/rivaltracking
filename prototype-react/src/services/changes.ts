/*
 * Change events are read-only from the frontend's perspective — detection
 * happens in the Python Change Detector. Future endpoints:
 *   GET /api/changes            (filtering/sorting/pagination server-side)
 *   GET /api/changes/:id
 * The list currently comes straight from mock data in the workspace store;
 * this module exists so the swap point is already in place.
 */

export {}
