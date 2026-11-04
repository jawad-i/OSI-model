CC ?= gcc
CFLAGS = -Wall -Wextra -O2 -Isrc

# OS detection
ifeq ($(OS),Windows_NT)
    LIBS = -lws2_32
    RM = del /Q /F
    EXT = .exe
else
    LIBS =
    RM = rm -f
    EXT =
endif

TARGETS = bin/osi_sim$(EXT) bin/osi_client$(EXT) bin/osi_server$(EXT)

all: dirs $(TARGETS)

dirs:
	@mkdir bin 2>nul || mkdir -p bin 2>/dev/null || true

bin/osi_layers.o: src/osi_layers.c src/osi_layers.h
	$(CC) $(CFLAGS) -c src/osi_layers.c -o bin/osi_layers.o

bin/osi_sim$(EXT): src/osi_simulation.c bin/osi_layers.o
	$(CC) $(CFLAGS) src/osi_simulation.c bin/osi_layers.o -o bin/osi_sim$(EXT) $(LIBS)

bin/osi_client$(EXT): src/client.c bin/osi_layers.o
	$(CC) $(CFLAGS) src/client.c bin/osi_layers.o -o bin/osi_client$(EXT) $(LIBS)

bin/osi_server$(EXT): src/server.c bin/osi_layers.o
	$(CC) $(CFLAGS) src/server.c bin/osi_layers.o -o bin/osi_server$(EXT) $(LIBS)

clean:
ifeq ($(OS),Windows_NT)
	-cmd /c "del /Q bin\*.o bin\*.exe 2>nul"
else
	rm -rf bin/*.o bin/*$(EXT)
endif

.PHONY: all dirs clean
