#include <moonlight/protocol.hpp>
#include <openssl/pem.h>
#include <memory>
#include <stdexcept>

using namespace moonlight;

void require(bool ok, const char *message) {
  if (!ok) throw std::runtime_error(message);
}

template <typename F> void must_fail(F action) {
  try { action(); } catch (const std::runtime_error &) { return; }
  throw std::runtime_error("malformed challenge accepted");
}

int main() {
  using Ptr = std::unique_ptr<EVP_PKEY, decltype(&EVP_PKEY_free)>;
  using Ctx = std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)>;
  using Bio = std::unique_ptr<BIO, decltype(&BIO_free)>;
  Ctx ctx(EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr), EVP_PKEY_CTX_free);
  require(ctx && EVP_PKEY_keygen_init(ctx.get()) == 1 && EVP_PKEY_CTX_set_rsa_keygen_bits(ctx.get(), 2048) == 1, "RSA setup failed");
  EVP_PKEY *raw = nullptr;
  require(EVP_PKEY_keygen(ctx.get(), &raw) == 1, "RSA generation failed");
  Ptr keypair(raw, EVP_PKEY_free);
  Bio private_bio(BIO_new(BIO_s_mem()), BIO_free), public_bio(BIO_new(BIO_s_mem()), BIO_free);
  require(private_bio && public_bio && PEM_write_bio_PrivateKey(private_bio.get(), raw, nullptr, nullptr, 0, nullptr, nullptr) == 1 && PEM_write_bio_PUBKEY(public_bio.get(), raw) == 1, "PEM encoding failed");
  char *data = nullptr;
  auto len = BIO_get_mem_data(private_bio.get(), &data);
  std::string private_key(data, len);
  len = BIO_get_mem_data(public_bio.get(), &data);
  std::string public_key(data, len);

  const std::string secret(16, 's'), challenge(16, 'c'), client_secret(16, 'p');
  const std::string cert_sig = "client certificate signature", server_sig = "server certificate signature";
  auto [phase1, key] = pair::get_server_cert("1234", "0011223344556677", "server cert");
  require(phase1.get<int>("root.paired") == 1, "phase 1 failed");
  const std::string client_challenge(16, 'q');
  auto enc_challenge = crypto::str_to_hex(crypto::aes_encrypt_ecb(client_challenge, key));
  auto [phase2, secrets] = pair::send_server_challenge(key, enc_challenge, server_sig, secret, challenge);
  require(phase2.get<int>("root.paired") == 1 && secrets.first == secret && secrets.second == challenge, "phase 2 failed");
  auto decrypted = crypto::aes_decrypt_ecb(crypto::hex_to_str(phase2.get<std::string>("root.challengeresponse"), true), key);
  auto expected = crypto::hex_to_str(crypto::sha256(client_challenge + server_sig + secret), true) + challenge;
  require(decrypted == expected, "phase 2 response mismatch");
  auto client_hash = crypto::hex_to_str(crypto::sha256(challenge + cert_sig + client_secret), true);
  auto response = crypto::str_to_hex(crypto::aes_encrypt_ecb(client_hash, key));
  auto [phase3, received_hash] = pair::get_client_hash(key, secret, response, private_key);
  require(phase3.get<int>("root.paired") == 1 && received_hash == client_hash, "phase 3 failed");
  auto proof = crypto::str_to_hex(client_secret + crypto::sign(client_secret, private_key));
  require(pair::client_pair(key, challenge, received_hash, proof, cert_sig, public_key).get<int>("root.paired") == 1, "phase 4 failed");
  must_fail([&] { pair::send_server_challenge(key, "0102030405060708090a0b0c0d0e0f", server_sig, secret, challenge); });
  must_fail([&] { pair::get_client_hash(key, secret, "0102030405060708090a0b0c0d0e0f", private_key); });
}
