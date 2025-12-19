import requests
import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import colorama
from colorama import Fore, Style

# تفعيل الألوان
colorama.init(autoreset=True)

API_TOKEN = None
BASE_URL = "https://oneurai.com/api"

# =====================================================
# 1. الدخول (Authentication)
# =====================================================
def login(token):
    global API_TOKEN
    API_TOKEN = token
    headers = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}
    
    print(f"""{Fore.CYAN}{Style.BRIGHT}
    ____                             _ 
   / __ \                           (_)
  | |  | |_ __   ___ _   _ _ __ __ _ _   
  | |  | | '_ \ / _ \ | | | '__/ _` | |  
  | |__| | | | |  __/ |_| | | | (_| | |  
   \____/|_| |_|\___|\__,_|_|  \__,_|_|  
                                         
      {Fore.GREEN}>> AI & MLOps Library <<{Style.RESET_ALL}
""")
    print(f"{Fore.CYAN}📡 Checking connection...{Style.RESET_ALL}")
    
    try:
        response = requests.get(f"{BASE_URL}/user", headers=headers, timeout=10)
        if response.status_code == 200:
            user = response.json()
            name = user.get('username') or user.get('name')
            print(f"{Fore.GREEN}✅ Connected successfully as: {name}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Warning: Could not fetch username (Code {response.status_code}).{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Connection Warning: {e}{Style.RESET_ALL}")

# =====================================================
# 2. الموديلات (Models)
# =====================================================
class SimpleNN(nn.Module):
    def __init__(self, layers_config):
        super(SimpleNN, self).__init__()
        layers = []
        for i in range(len(layers_config) - 1):
            layers.append(nn.Linear(layers_config[i], layers_config[i+1]))
            if i < len(layers_config) - 2:
                layers.append(nn.ReLU())
            else:
                layers.append(nn.Sigmoid())
        self.model = nn.Sequential(*layers)
        self.config = layers_config

    def forward(self, x):
        return self.model(x)

    def train_model(self, X, y, epochs=1000):
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.parameters(), lr=0.01)
        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32)
        print(f"\n{Fore.MAGENTA}🚀 Training...{Style.RESET_ALL}")
        for _ in tqdm(range(epochs), desc="Epochs", colour='green'):
            optimizer.zero_grad()
            outputs = self(X_t)
            loss = criterion(outputs, y_t)
            loss.backward()
            optimizer.step()
        print(f"{Fore.GREEN}✅ Done.{Style.RESET_ALL}")

    def save(self, path):
        torch.save({'state_dict': self.state_dict(), 'config': self.config}, path)

    def load(self, path):
        checkpoint = torch.load(path)
        self.load_state_dict(checkpoint['state_dict'])
        self.config = checkpoint['config']
        self.eval()

class Model:
    def __init__(self, layers):
        self.engine = SimpleNN(layers)
    
    def train(self, X, y, epochs=1000):
        self.engine.train_model(X, y, epochs)

    def predict(self, val):
        with torch.no_grad():
            return self.engine(torch.tensor(val, dtype=torch.float32)).tolist()

    # دالة الرفع الخاصة بالكلاس (Instance Method)
    def push_to_hub(self, full_repo_name, description="AI Model uploaded via Oneurai"):
        if "/" not in full_repo_name:
            print(f"{Fore.RED}❌ Format Error: Use 'username/project_name'{Style.RESET_ALL}")
            return
        _, repo_name = full_repo_name.split("/", 1)
        filename = f"{repo_name}.pt"
        self.engine.save(filename)
        _upload_file(full_repo_name, filename, "models", description)
        if os.path.exists(filename): os.remove(filename)

# --- دوال عامة للموديلات ---
def create_model(layers):
    return Model(layers)

def load_model(full_repo_name, layers):
    _, repo_name = full_repo_name.split("/", 1)
    filename = f"{repo_name}.pt"
    url = f"{BASE_URL}/models/{full_repo_name}/download/{filename}"
    return _download_and_load_model(url, filename, layers)

# ⚠️ هذه هي الدالة المفقودة التي تصلح الخطأ في test.py
def push_to_hub(repo_id, model, description="Uploaded Model"):
    """
    دالة عامة لرفع المودل (تغلف دالة الكلاس)
    """
    if hasattr(model, 'push_to_hub'):
        model.push_to_hub(repo_id, description)
    else:
        print(f"{Fore.RED}❌ Error: Object provided is not a valid Oneurai Model.{Style.RESET_ALL}")

# =====================================================
# 3. إدارة البيانات والمستودعات
# =====================================================
def upload_dataset(file_path, full_repo_name, description="Dataset"):
    if not os.path.exists(file_path):
        print(f"{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
        return
    print(f"📦 Preparing dataset: {file_path} ...")
    _upload_file(full_repo_name, file_path, "datasets", description)

def download_dataset(full_repo_name, filename, save_path=None):
    if save_path is None: save_path = filename
    url = f"{BASE_URL}/datasets/{full_repo_name}/download/{filename}"
    _download_file(url, save_path)

def upload_to_repo(file_path, full_repo_name, description="Repo File"):
    if not os.path.exists(file_path):
        print(f"{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
        return
    print(f"📂 Preparing repo file: {file_path} ...")
    _upload_file(full_repo_name, file_path, "repos", description)

def download_from_repo(full_repo_name, filename, save_path=None):
    if save_path is None: save_path = filename
    url = f"{BASE_URL}/repos/{full_repo_name}/download/{filename}"
    _download_file(url, save_path)

# =====================================================
# 🔧 دوال المساعدة (Helpers)
# =====================================================
def _upload_file(full_repo_name, file_path, type_category, description):
    if "/" not in full_repo_name:
        print(f"{Fore.RED}❌ Format Error: Use 'username/project_name'{Style.RESET_ALL}")
        return

    username, repo_name = full_repo_name.split("/", 1)
    url = f"{BASE_URL}/{type_category}/{username}/{repo_name}/upload"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    data = {'description': description}
    
    print(f"☁️ Uploading to [{type_category.upper()}] -> {Fore.BLUE}{full_repo_name}{Style.RESET_ALL} ...")
    
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, files={'file': f}, data=data)
        
        if response.status_code in [200, 201]:
            print(f"{Fore.GREEN}✅ Upload Successful!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Server Error ({response.status_code}): {response.text}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Connection Failed: {e}{Style.RESET_ALL}")

def _download_file(url, save_path):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            with open(save_path, 'wb') as f: f.write(r.content)
            print(f"{Fore.GREEN}✅ Downloaded: {save_path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed: {r.status_code}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")

def _download_and_load_model(url, filename, layers):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            with open(filename, 'wb') as f: f.write(r.content)
            m = Model(layers)
            m.engine.load(filename)
            print(f"{Fore.GREEN}✅ Model loaded successfully.{Style.RESET_ALL}")
            os.remove(filename)
            return m
        else:
            print(f"{Fore.RED}❌ Failed: {r.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        return None