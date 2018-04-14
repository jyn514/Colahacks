CC=g++

bin/main: build/main.o
	$(CC) $^ -o bin/main

build/main.o: src/main.cpp
	$(CC) -c $< -o $@

clean:
	@rm -f bin/* build/*
