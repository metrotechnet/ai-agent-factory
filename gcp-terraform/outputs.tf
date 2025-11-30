output "service_account_email" {
  value = google_service_account.sa.email
}

output "firestore_location" {
  value = google_firestore_database.default.location_id
}

