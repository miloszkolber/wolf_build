#include <crypto/crypto.hpp>
#include <openssl/x509v3.h>
#include <cstdlib>
#include <stdexcept>
#include <string>

static void require(bool condition, const char *message) {
  if (!condition) throw std::runtime_error(message);
}

static x509::x509_ptr issued(x509::x509_ptr issuer, x509::pkey_ptr signing_key) {
  auto key = x509::generate_key();
  auto cert = x509::x509_ptr(X509_new(), X509_free);
  require(cert && ASN1_INTEGER_set(X509_get_serialNumber(cert.get()), 2) &&
              X509_set_version(cert.get(), 2) && X509_gmtime_adj(X509_get_notBefore(cert.get()), 0) &&
              X509_gmtime_adj(X509_get_notAfter(cert.get()), 3600) && X509_set_pubkey(cert.get(), key.get()),
          "cannot build client certificate");
  require(X509_NAME_add_entry_by_txt(X509_get_subject_name(cert.get()), "CN", MBSTRING_ASC,
                                     (const unsigned char *)"client", -1, -1, 0) &&
              X509_set_issuer_name(cert.get(), X509_get_subject_name(issuer.get())) &&
              X509_sign(cert.get(), signing_key.get(), EVP_sha256()),
          "cannot sign client certificate");
  return cert;
}

int main() {
  auto paired_key = x509::generate_key();
  auto paired = x509::generate_x509(paired_key);
  auto unrelated_key = x509::generate_key();
  auto unrelated = x509::generate_x509(unrelated_key);
  require(!x509::verification_error(paired, paired), "paired certificate rejected");
  require(!x509::verification_error(unrelated, unrelated), "second paired certificate rejected");
  require(x509::verification_error(paired, unrelated).has_value(), "unpaired self-signed certificate accepted");
  require(x509::verification_error(unrelated, paired).has_value(), "first client matched second paired record");

  auto forged = issued(unrelated, unrelated_key);
  X509_NAME *unknown = X509_NAME_new();
  require(unknown && X509_NAME_add_entry_by_txt(unknown, "CN", MBSTRING_ASC,
                                                 (const unsigned char *)"unknown issuer", -1, -1, 0) &&
              X509_set_issuer_name(forged.get(), unknown) &&
              X509_sign(forged.get(), unrelated_key.get(), EVP_sha256()), "cannot construct unknown issuer");
  X509_NAME_free(unknown);
  auto error = x509::verification_error(paired, forged);
  require(error && *error == "unable to get local issuer certificate", "unknown issuer accepted");
  require(x509::verification_error(unrelated, forged).has_value(), "unknown issuer matched second paired record");
  require(setenv("WOLF_ALLOW_UNKNOWN_ISSUER_CERTS", "TRUE", 1) == 0 &&
              x509::verification_error(paired, forged).has_value(), "environment restored unsafe issuer bypass");

  // Preserve the existing partial-chain policy, rather than introducing exact-certificate pinning.
  auto ca_key = x509::generate_key();
  auto paired_ca = x509::generate_x509(ca_key);
  X509_EXTENSION *ca = X509V3_EXT_conf_nid(nullptr, nullptr, NID_basic_constraints, (char *)"critical,CA:TRUE");
  require(ca && X509_add_ext(paired_ca.get(), ca, -1) && X509_sign(paired_ca.get(), ca_key.get(), EVP_sha256()),
          "cannot construct paired CA");
  X509_EXTENSION_free(ca);
  auto child = issued(paired_ca, ca_key);
  auto chain_error = x509::verification_error(paired_ca, child);
  if (chain_error) throw std::runtime_error("paired issuer chain rejected: " + *chain_error);
  auto bad_signature = issued(paired_ca, unrelated_key);
  require(x509::verification_error(paired_ca, bad_signature).has_value(), "incorrect issuer signature accepted");
  require(X509_gmtime_adj(X509_get_notAfter(child.get()), -3600) &&
              X509_sign(child.get(), ca_key.get(), EVP_sha256()), "cannot construct expired client");
  require(!x509::verification_error(paired_ca, child), "existing expired-certificate tolerance changed");
}
