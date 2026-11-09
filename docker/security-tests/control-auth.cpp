#include <moonlight/control.hpp>
#include <stdexcept>
#include <string>
#include <cstring>

using namespace moonlight::control;

template <typename F> void must_reject(F action) {
  try {
    action();
  } catch (const std::runtime_error &) {
    return;
  }
  throw std::runtime_error("tampered packet was accepted");
}

int main() {
  const std::string key = "00112233445566778899AABBCCDDEEFF";
  const std::string other = "10112233445566778899AABBCCDDEEFF";
  const std::string payload("\x02\x03\x00\x00", 4);
  auto packet = encrypt_packet(key, 0, payload);
  if (decrypt_packet(*packet, key) != payload)
    throw std::runtime_error("valid control packet failed");
  packet->gcm_tag[0] ^= 1;
  must_reject([&] { decrypt_packet(*packet, key); });
  packet->gcm_tag[0] ^= 1;
  packet->payload[0] ^= 1;
  must_reject([&] { decrypt_packet(*packet, key); });
  packet->payload[0] ^= 1;
  must_reject([&] { decrypt_packet(*packet, other); });
  must_reject([&] { crypto::aes_decrypt_gcm("x", std::string(16, 'k'), "short", std::string(16, 'i'), 16); });
  must_reject([&] { crypto::aes_decrypt_gcm("x", std::string(16, 'k'), std::string(16, 't'), std::string(16, 'i'), 0); });
  must_reject([&] { crypto::aes_encrypt_gcm("x", std::string(16, 'k'), std::string(16, 'i'), 0); });
  bool with_nul = false, without_nul = false;
  for (unsigned seq = 0; seq < 256; ++seq) {
    auto candidate = encrypt_packet(key, seq, payload);
    bool has_nul = std::memchr(candidate->gcm_tag, 0, GCM_TAG_SIZE) != nullptr;
    with_nul |= has_nul;
    without_nul |= !has_nul;
    if (decrypt_packet(*candidate, key) != payload)
      throw std::runtime_error("binary GCM tag failed");
  }
  if (!with_nul || !without_nul)
    throw std::runtime_error("test vectors did not cover both binary tag forms");
  const std::string aes_key(16, 'k'), iv(16, 'i');
  const std::string plain = "valid pairing and audio data";
  auto encrypted = crypto::aes_encrypt_cbc(plain, aes_key, iv, true);
  if (crypto::aes_decrypt_cbc(encrypted, aes_key, iv, true) != plain)
    throw std::runtime_error("valid CBC roundtrip failed");
  must_reject([&] { crypto::aes_decrypt_ecb(std::string(15, 'x'), aes_key, iv, false); });
  must_reject([&] { crypto::sign(plain, "invalid private key"); });
  if (crypto::verify(plain, "signature", "invalid public key"))
    throw std::runtime_error("invalid public key verified");
}
