/* Use the image's own ALSA libraries without installing development libraries. */
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    void *lib = dlopen("libasound.so.2", RTLD_NOW), *pcm = NULL;
    if (!lib) { fprintf(stderr, "%s\n", dlerror()); return 1; }
    int (*open_pcm)(void **, const char *, int, int) = dlsym(lib, "snd_pcm_open");
    int (*params)(void *, int, int, unsigned, unsigned, int, unsigned) = dlsym(lib, "snd_pcm_set_params");
    long (*write_pcm)(void *, const void *, unsigned long) = dlsym(lib, "snd_pcm_writei");
    int (*drain)(void *) = dlsym(lib, "snd_pcm_drain");
    int (*close_pcm)(void *) = dlsym(lib, "snd_pcm_close");
    int (*open_ctl)(void **, const char *, int) = dlsym(lib, "snd_ctl_open");
    int (*close_ctl)(void *) = dlsym(lib, "snd_ctl_close");
    if (!open_pcm || !params || !write_pcm || !drain || !close_pcm || !open_ctl || !close_ctl) return 1;
    void *ctl = NULL;
    if (open_ctl(&ctl, "default", 0) < 0 || close_ctl(ctl) < 0) return 1;
    /* S16_LE, RW_INTERLEAVED, stereo, 48 kHz, 100 ms latency. */
    if (open_pcm(&pcm, "default", 0, 0) < 0 || params(pcm, 2, 3, 2, 48000, 1, 100000) < 0) return 1;
    short samples[960 * 2];
    for (int i = 0; i < 960; i++) samples[i * 2] = samples[i * 2 + 1] = i % 100 < 50 ? 10000 : -10000;
    for (int block = 0; block < 100; block++) {
        unsigned long offset = 0;
        while (offset < 960) {
            long n = write_pcm(pcm, samples + offset * 2, 960 - offset);
            if (n <= 0) return 1;
            offset += n;
        }
    }
    if (drain(pcm) < 0 || close_pcm(pcm) < 0) return 1;
    puts("ALSA_DEFAULT_PLAYBACK_PASS");
    return 0;
}
