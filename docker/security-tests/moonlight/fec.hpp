#pragma once
#include <cstdint>
#include <memory>
namespace moonlight::fec {
using rs_ptr = std::shared_ptr<int>;
inline int encode(int *, uint8_t **, int, int) { return 0; }
}
