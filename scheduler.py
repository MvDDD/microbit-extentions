import os
import threading
import time
import inspect
import asyncio
from typing import Callable, Any

class Scheduler:
def init(self, resolution=0):
self._lock = threading.Lock()
self._tasks: list[dict] = []
self._running_tasks: list[dict] = []
self._running = False
self._loop_thread: threading.Thread | None = None
self._resolution = resolution
self.done_task_indices = []
self.finished_task_indices = []
self.__finished_task_indices = []

def _now_ms(self) -> int:  
	return int(time.time() * 1000)  
def __call__(self, *a, **k):  
	return self.add(*a, **k)  
def add(self, callback: Callable[[], Any],  
		timeout: int | None = None,  
		interval: int | str | None = None) -> Callable[[], None] | None:  
	"""Schedule a generator callback."""  
	if not inspect.isgeneratorfunction(callback):  
		raise TypeError("callback must be a generator function")  

	# normalize interval  
	if isinstance(interval, str) and interval.upper() == "B2B":  
		interval_norm = "B2B"  
	elif interval is None:  
		interval_norm = None  
	else:  
		interval_norm = int(interval)  

	now = self._now_ms()  
	first = None  
	if interval_norm in (None, "B2B"):  
		first = now + int(timeout) if timeout is not None else (now if interval_norm == "B2B" else now)  
	else:  
		first = now + int(timeout) if timeout is not None else now  

	with self._lock:  
		idx = len(self._tasks)  
		self._tasks.append({  
			'callback': callback,  
			'interval': interval_norm,  
			'next': (None if interval_norm in (None, "B2B") and timeout is None else first)  
		})  
	  

	reset = None  
	if isinstance(interval_norm, int):  
		def reset():  
			with self._lock:  
				if 0 <= idx < len(self._tasks) and self._tasks[idx] is not None:  
					self._tasks[idx]['next'] = self._now_ms() + interval_norm  
	def remove():  
		self.__finished_task_indices.append(idx)  
	return [reset or None, remove]  

def tick(self):  
	"""Step the scheduler once (non-blocking)."""  
	now = self._now_ms()  
	self.finished_task_indices.extend(self.__finished_task_indices)  
	self.__finished_task_indices.clear()  

	# Step running generators  
	running_snapshot = list(self._running_tasks)  
	for rt in running_snapshot:  
		gen = rt['gen']  
		idx = rt['task_index']  
		try:  
			next(gen)  
		except StopIteration as e:  
			with self._lock:  
				if idx >= len(self._tasks) or self._tasks[idx] is None:  
					if rt in self._running_tasks:  
						self._running_tasks.remove(rt)  
					continue  
				interval = self._tasks[idx]['interval']  

			if interval == "B2B":  
				try:  
					rt['gen'] = rt['callback']()  
				except Exception:  
					self.finished_task_indices.append(idx)  
			elif interval is None or (hasattr(e, 'value') and e.value is False):  
				self.finished_task_indices.append(idx)  
			else:  
				self.done_task_indices.append(idx)  

	if self.done_task_indices:  
		self._running_tasks[:] = [r for r in self._running_tasks if r['task_index'] not in self.done_task_indices]  

	# Schedule new generators  
	with self._lock:  
		for i, task in enumerate(list(self._tasks)):  
			if task is None:  
				continue  
			if any(r['task_index'] == i for r in self._running_tasks):  
				continue  

			interval = task['interval']  
			next_call = task['next']  
			due = False  

			if interval == "B2B":  
				due = True  
			elif interval is None:  
				if next_call is None or now >= next_call:  
					due = True  
			else:  
				if next_call is not None and now >= next_call:  
					due = True  

			if due:  
				try:  
					gen = task['callback']()  
				except Exception:  
					continue  

				self._running_tasks.append({  
					'gen': gen,  
					'task_index': i,  
					'callback': task['callback']  
				})  
				if isinstance(interval, int):  
					self._tasks[i]['next'] += interval + 0.0001  

	# Remove finished tasks  
	if self.finished_task_indices:  
		with self._lock:  
			for index in sorted(self.finished_task_indices, reverse=True):  
				if 0 <= index < len(self._tasks):  
					self._tasks.pop(index)  
	self.finished_task_indices.clear()  
	self.done_task_indices.clear()  
	if self._resolution:  
		time.sleep(self._resolution*1000)  
	return len(self._tasks)  

def tickloop(self):  
	a=1  
	while a:  
		a = yield self.tick()  

def _run_loop(self):  
	self._running = True  
	while self._running and (self._tasks or self._running_tasks):  
		self.tick()  
	self._running_tasks.clear()  
	self._tasks.clear()  
	self._running = False  

def run_sync(self):  
	"""Blocking execution."""  
	self._run_loop()  

def run_async(self):  
	"""Run in a separate daemon thread."""  
	if self._running_thread_alive():  
		return  
	self._loop_thread = threading.Thread(target=self._run_loop, daemon=True)  
	self._loop_thread.start()  

def stop(self):  
	"""Stop the scheduler."""  
	self._running = False  
	if self._loop_thread:  
		self._loop_thread.join(timeout=0.1)  

def _running_thread_alive(self):  
	return self._loop_thread and self._loop_thread.is_alive()

----------------- Helpers -----------------

def seconds(n): return int(n1000)
def minutes(n): return seconds(60n)
def hours(n): return minutes(60n)
def days(n): return hours(24n)
def weeks(n): return days(7n)
def years(n): return days(365.25n)

def sleep(ms):
start = time.time()
end = start + ms/1000
current = start
while (current := time.time()) < end:
yield
return current - start

class YieldLock:
def init(self):
self._lock = threading.Lock()
self._locked = False

def acquire(self):  
	"""Generator: yields until the lock can be acquired."""  
	while True:  
		with self._lock:  
			if not self._locked:  
				self._locked = True  
				break  
		yield  # lock busy, yield to scheduler  
	yield  # final yield after acquiring  

def release(self):  
	with self._lock:  
		self._locked = False  

def __enter__(self):  
	return self.acquire()  # returns generator  

def __exit__(self, exc_type, exc_val, exc_tb):  
	self.release()

class aopen:
i = 0
def init(self, path, mode="rb", encoding="utf-8"):
"""
mode: "r", "w", "a", "rb", "wb", "ab", etc.
encoding: used for text modes (ignored for binary)
"""

flags = 0  
	if "r" in mode:  
		flags |= os.O_RDONLY  
	if "w" in mode:  
		flags |= os.O_WRONLY | os.O_CREAT | os.O_TRUNC  
	if "a" in mode:  
		flags |= os.O_WRONLY | os.O_CREAT | os.O_APPEND  

	flags |= os.O_NONBLOCK  
	self.mode = mode  
	self.flags = flags  
	self.path = path  
	self.encoding = encoding  
	self.is_text = "b" not in mode  
	self.isOpen = 0  
	self._write_buffer = b""  

def open(self):  
	while aopen.i >= 40:  
		yield  
	aopen.i += 1  
	self.fd = os.open(self.path, self.flags)  
	self.isOpen = 1  
# ---------------- read ----------------  
def aread(self, size=4096):  
	data = b""  
	while size > 0:  
		try:  
			chunk = os.read(self.fd, min(size, 4096))  
			if not chunk:  
				break  
			data += chunk  
			size -= len(chunk)  
		except BlockingIOError:  
			yield  
			continue  
	if self.is_text:  
		return data.decode(self.encoding)  
	return data  

def read(self, size=4096):  
	data = b""  
	while size > 0:  
		try:  
			chunk = os.read(self.fd, min(size, 4096))  
			if not chunk:  
				break  
			data += chunk  
			size -= len(chunk)  
		except BlockingIOError:  
			time.sleep(0.00001)  
			continue  
	if self.is_text:  
		return data.decode(self.encoding)  
	return data  

# ---------------- write buffer ----------------  
def awrite(self, data):  
	"""  
	Generator: buffer data and write nonblocking.  
	Accepts str in text mode, bytes in binary mode.  
	"""  
	if self.is_text:  
		data = data.encode(self.encoding)  
	self._write_buffer += data  
	while self._write_buffer:  
		try:  
			written = os.write(self.fd, self._write_buffer)  
			self._write_buffer = self._write_buffer[written:]  
		except BlockingIOError:  
			yield  
			continue  
		yield  

# ---------------- flush ----------------  
def flush(self):  
	while self._write_buffer:  
		try:  
			written = os.write(self.fd, self._write_buffer)  
			self._write_buffer = self._write_buffer[written:]  
		except BlockingIOError:  
			yield  
			continue  
		yield  
	# optionally fsync  
	# os.fsync(self.fd)  

# ---------------- sync write ----------------  
def write(self, data):  
	if self.is_text:  
		data = data.encode(self.encoding)  
	os.write(self.fd, data)  

# ---------------- close ----------------  
def close(self):  
	if self.isOpen:  
		[*self.flush()]  
		os.close(self.fd)  
		aopen.i -= 1  
	else:  
		pass  

def __enter__(self):  
	return self  
def __exit__(self, _0, _1, _2):  
	self.close()

import multiprocessing

def arun(func, *args, **kwargs):
def _run_target(func, args, kwargs, result_queue):
"""Internal target for running a blocking function in a separate process."""
try:
res = func(*args, **kwargs)
result_queue.put((True, res))
except Exception as e:
result_queue.put((False, e))
"""
Run a blocking function asynchronously in a separate process.
Returns a generator that yields until the process finishes.
Usage:
for done, result in arun(blocking_func, arg1, arg2):
pass  # scheduler can tick other tasks
# After completion, result contains the function's return value or exception
"""
result_queue = multiprocessing.Queue()
proc = multiprocessing.Process(target=_run_target, args=(func, args, kwargs, result_queue))
proc.start()

while proc.is_alive():  
	yield  # yield to scheduler  
proc.join()  

success, result = result_queue.get()  
if success:  
	return result  
else:  
	raise result
