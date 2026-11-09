#pragma once
namespace logs {
enum level { warning };
template <typename... T> void log(level, const char *, T&&...) {}
}
