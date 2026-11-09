#include <gst-plugin/audio.hpp>
#include <stdexcept>
#include <string>

static void require(bool value, const char *message) {
  if (!value) throw std::runtime_error(message);
}

int main() {
  gst_init(nullptr, nullptr);
  gst_rtp_moonlight_pay_audio pay{};
  unsigned char storage[AUDIO_TOTAL_SHARDS][AUDIO_MAX_BLOCK_SIZE]{};
  unsigned char *shards[AUDIO_TOTAL_SHARDS]{};
  for (int i = 0; i < AUDIO_TOTAL_SHARDS; ++i) shards[i] = storage[i];
  pay.packets_buffer = shards;
  pay.encrypt = true;
  pay.encrypt_failed = false;
  pay.aes_key = "0123456789012345";
  pay.aes_iv = "12345";
  pay.packet_duration = 5;
  const std::string sample = "valid audio payload";
  GstBuffer *input = gst_buffer_new_and_fill(sample.size(), sample.c_str());
  GstBufferList *output = audio::split_into_rtp(&pay, input);
  require(gst_buffer_list_length(output) == 1 && pay.cur_seq_number == 1, "valid audio not packetized");
  GstBuffer *packet = gst_buffer_list_get(output, 0);
  auto bytes = gst_buffer_copy_content(packet);
  std::string encrypted(bytes.begin() + audio::RTP_HEADER_SIZE, bytes.end());
  require(crypto::aes_decrypt_cbc(encrypted, pay.aes_key, derive_iv(pay.aes_iv, 0), true) == sample, "audio ciphertext mismatch");
  gst_buffer_list_unref(output);
  pay.aes_iv = "invalid";
  for (int i = 0; i < 2; ++i) {
    output = audio::split_into_rtp(&pay, input);
    require(gst_buffer_list_length(output) == 0 && pay.cur_seq_number == 1 && pay.encrypt_failed, "invalid audio IV not dropped");
    gst_buffer_list_unref(output);
  }
  gst_buffer_unref(input);
}
