from datetime import datetime,timedelta
import time
import os
import ctypes
import pandas as pd
import json
import pyautogui as pag

def enable_virtual_terminal():
    if os.name == 'nt':  # Windows
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, mode)

def clear_terminal(lines:int=1,length:int=100) -> None:
    for _ in range(lines):
        print('\033[A'+' '*length,'\033[A')

def write_to_excel(dataframe:pd.DataFrame,output_path:str,print_decorators:bool=True) -> None:
    print('WRITING TO EXCEL') if print_decorators else None
    with pd.ExcelWriter(output_path) as writer:
        dataframe.to_excel(writer, index=False)
    print(' Success') if print_decorators else None

def add_to_memory(memory_key:str, new_entry:dict) -> None:
    def validate_new_entry(new_entry:dict):
        if not len(data[memory_key]) == 0:
            if data[memory_key][0].keys() != new_entry.keys():
                raise KeyError(f'Dict structure of new entry does not match existing structure in {memory_key}')
        if 'id' not in new_entry.keys():
            raise KeyError(f'Key "id" must be in new entries')
    
    memory_path = r'memory\memory.json'
    if not os.path.isfile(memory_path):
        data = {}
    else:
        with open(memory_path,'r') as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = {}
    
    if memory_key not in data.keys():
        data[memory_key] = []
    
    validate_new_entry(new_entry)
    data[memory_key] = [entry for entry in data[memory_key] if entry['id'] != new_entry['id']] # removes existing entry from memory before adding new entry
    data[memory_key].append(new_entry)

    os.makedirs(os.path.dirname(memory_path), exist_ok=True)
    with open(memory_path, 'w') as file:
        json.dump(data, file, indent=2)

def is_in_memory(memory_key:str,new_entry:dict,comparison_field:str) -> bool:
    def validate_new_entry(new_entry:dict):
        if data[memory_key][0].keys() != new_entry.keys():
            raise KeyError(f'Dict structure of new entry does not match existing structure in {memory_key}')
        if comparison_field not in data[memory_key][0].keys():
            raise KeyError(f'Comparison field "{comparison_field}" not found in existing entries')
        if comparison_field not in new_entry.keys():
            raise KeyError(f'Comparison field "{comparison_field}" not found in new entry')
        if 'id' not in new_entry.keys():
            raise KeyError(f'Key "id" must be in new entries')
    
    memory_path = r'memory\memory.json'
    if not os.path.isfile(memory_path):
        return False
    
    with open(memory_path,'r') as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            return False
        
    if memory_key not in data.keys():
        return False
    
    validate_new_entry(new_entry)
    for entry in data[memory_key]:
        if entry['id'] == new_entry['id'] and entry[comparison_field] == new_entry[comparison_field]:
            return True
    
    return False

def wait_for_image(image_path:str|list,timeout:int=5,interval:float=0.1,conf:float=0.95,invert_search=False) -> tuple:
    start_time = time.time()
    coord = None
    printed = False
    
    imgs = []
    if isinstance(image_path,str):
        imgs.append(image_path)
        image_path = imgs
    
    if isinstance(image_path,list):
        while coord is None:
            if (time.time() - start_time) < timeout:
                pass
            else:
                if not printed:
                    if not invert_search:
                        print(f' - Unable to locate {[os.path.split(img)[1] for img in image_path]}')
                    else:
                        print(f' - Waiting for {[os.path.split(img)[1] for img in image_path]} to close')
                    printed = True
            
            for img in image_path:
                if not invert_search:
                    try:
                        coord = pag.locateCenterOnScreen(img,grayscale=True,confidence=conf)
                    except pag.ImageNotFoundException:
                        pass
                else:
                    try:
                        coord = pag.locateCenterOnScreen(img,grayscale=True,confidence=conf)
                    except pag.ImageNotFoundException:
                        coord = True
                
                time.sleep(interval)
        if printed:
            clear_terminal()
        return coord
    else:
        raise TypeError(f'Unsupported image_path type: {type(image_path)}')
    
def find_and_click(image_path:str,offset:tuple=(0,0)) -> None:
    coord = wait_for_image(image_path)
    coord = offset_coords(coord,offset)
    pag.sleep(0.25)
    pag.click(coord)
    pag.sleep(0.25)

def offset_coords(coords:tuple[int,int],offset:tuple[int,int]=(0,0)) -> tuple[int,int]:
    x,y = coords
    x_off,y_off = offset

    return (x+x_off,y+y_off)

class Counter:
    def __init__(self,count,max_completion_n=10,format=None):
        self.n:int = 0
        self.count:int = count
        self.formatter:str = format
        self.times_to_complete = []
        self.start_times = []
        self.max_completion_n = max_completion_n
    
    @property
    def default(self):
        return f"{self.n}/{self.count}"
    
    @property
    def formatted(self):
        formatting_map = {
            '%n':self.n,
            '%N':self.count,
            '%T':self.completion_time,
            '%t':self.time_remaining(),
            '%f':self.time_remaining(formatted=True)
        }

        formatting_str = self.formatter
        for key,value in formatting_map.items():
            if value is None:
                formatting_str = formatting_str.replace(key,'')
            else:
                formatting_str = formatting_str.replace(key,f'{value}')
        
        return formatting_str
    
    @property
    def completion_time(self):
        if self.time_remaining() is not None:
            exp_end_time = datetime.fromtimestamp(datetime.now().timestamp() + self.time_remaining())
            return exp_end_time.strftime('%I:%M %p')
        else:
            return None
    
    def _format_time(self,seconds):
        secs = int(seconds)
        hr = secs // 3600
        mins = (secs % 3600) // 60
        sec = secs % 60
        return f'{hr}h {mins}m {sec}s'
    
    def time_remaining(self,formatted = False):
        if not self.times_to_complete:
            return None
        
        count_remaining = self.count - self.n
        avg_time = (sum(self.times_to_complete) / len(self.times_to_complete))
        seconds = avg_time * count_remaining

        if formatted:
            return self._format_time(seconds)
        else:
            return round(seconds,2)

    def display(self):
        self.start_times.append(datetime.now())

        if len(self.start_times) > 1:
            self.times_to_complete.append(self.start_times[-1].timestamp() - self.start_times[-2].timestamp())
            if len(self.times_to_complete) > self.max_completion_n:
                self.times_to_complete = self.times_to_complete[-self.max_completion_n:]

        self.n += 1
        if self.formatter:
            print(self.formatted)
        else:
            print(self.default)

def get_most_recent_file(directory: str) -> str:
    # List comprehension to get all files in the passed directory (excluding subdirectories)
    files = [os.path.join(directory, file) for file in os.listdir(directory) 
             if os.path.isfile(os.path.join(directory, file))]

    # Return the most recently created file using max and os.path.getctime
    return max(files, key=os.path.getctime) if files else "No files found"
        
def __main():
    ...

if __name__ == '__main__':
    __main()
