import requests


class IsingClientError(Exception):
    """Ising SDK 异常类"""
    pass


class AuthenticationError(IsingClientError):
    """认证错误异常类"""
    pass


class IsingClient:
    def __init__(self, api_key=None, base_url="https://api.isingq.com"):
        """
        初始化SDK客户端

        :param api_key: 认证密钥
        :param base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()

    def _request(self, method, endpoint, **kwargs):
        """内部请求方法"""
        url = f"{self.base_url}/{endpoint}"
        headers = kwargs.get('headers', {})
        headers['Authorization'] = self.api_key
        headers['channel'] = "sdk"
        kwargs['headers'] = headers

        try:
            response = self.session.request(method, url, **kwargs)
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed: Invalid API key")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise IsingClientError(f"API request failed: {str(e)}")

    def get_task(self, task_id):
        """获取资源"""
        return self._request('GET', f'tasks/{task_id}')

    def get_task_list(self, page_no=1, page_size=10):
        """
        获取任务列表

        :param page_no: 页码
        :param page_size: 每页数量
        :return: API响应数据
        """
        return self._request('POST', 'tasks/list', json={'page_no': page_no, 'page_size': page_size})


    def create_general_task(self, request):
        """
        创建通用任务
        
        :param request: GeneralTaskCreateRequest 对象
        :return: API响应数据
        """
        return self._request('POST', 'tasks/create-general', json=request.to_dict())


    def create_template_task(self, request):
        """
        创建模板任务

        :param request: TemplateTaskCreateRequest 对象
        :return: API响应数据
        """
        return self._request('POST', 'tasks/create-template', json=request.to_dict())


    def upload_file(self, file_bytes, original_filename=None):
        url = f"{self.base_url}/files/upload-bytes"
        headers = {}
        headers['Authorization'] = self.api_key
        headers['channel'] = "sdk"

        params = {}
        if original_filename:
            params['originalFilename'] = original_filename

        try:
            response = requests.post(url, data=file_bytes, params=params, headers=headers)
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed: Invalid API key")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise IsingClientError(f"API request failed: {str(e)}")
            

    def upload_file_to_oss(self, file_path_or_bytes, original_filename=None):
        """
        上传文件到OSS存储
        
        :param file_path_or_bytes: 文件路径(str)或文件字节数据(bytes)
        :param original_filename: 原始文件名，当传入bytes时必须提供
        :return: 包含文件URL的响应数据
        """
        import uuid
        import os
        
        # 处理文件输入
        if isinstance(file_path_or_bytes, str):
            # 文件路径
            if not os.path.exists(file_path_or_bytes):
                raise IsingClientError(f"File not found: {file_path_or_bytes}")
            
            with open(file_path_or_bytes, 'rb') as f:
                file_data = f.read()
            
            if original_filename is None:
                original_filename = os.path.basename(file_path_or_bytes)
        elif isinstance(file_path_or_bytes, bytes):
            # 字节数据
            if original_filename is None:
                raise IsingClientError("original_filename is required when uploading bytes data")
            file_data = file_path_or_bytes
        else:
            raise IsingClientError("file_path_or_bytes must be str (file path) or bytes")

        try:
            # 步骤1: 获取OSS上传签名
            headers = {}
            headers['Authorization'] = self.api_key
            headers['channel'] = "sdk"

            signature_response = requests.get(f"{self.base_url}/files/getPostSignatureForOssUpload", headers=headers).json()
            signature_data = signature_response['data']
            
            # 步骤2: 构建OSS上传表单数据
            form_data = {}
            
            # 生成唯一的文件key
            file_uuid = str(uuid.uuid4())[:8]
            file_key = f"{file_uuid}/{original_filename}"
            
            # 按照OSS要求的顺序添加表单字段
            form_data['success_action_status'] = '200'
            form_data['policy'] = signature_data['policy']
            form_data['x-oss-signature'] = signature_data['signature']
            form_data['x-oss-signature-version'] = 'OSS4-HMAC-SHA256'
            form_data['x-oss-credential'] = signature_data['x_oss_credential']
            form_data['x-oss-date'] = signature_data['x_oss_date']
            form_data['key'] = file_key
            form_data['x-oss-security-token'] = signature_data['security_token']
            
            # 准备multipart/form-data
            files = {'file': (original_filename, file_data)}
            
            # 步骤3: 上传到OSS
            oss_response = requests.post(
                signature_data['host'],
                data=form_data,
                files=files,
                headers=headers
            )
            
            if oss_response.status_code == 401:
                raise AuthenticationError("Authentication failed: Invalid API key")
            elif oss_response.status_code != 200:
                raise IsingClientError(f"OSS upload failed with status {oss_response.status_code}: {oss_response.text}")
            
            # 构建文件URL
            file_url = f"{signature_data['host']}/{file_key}"
            data = {
                "fileUrl": file_url,
                "originalFileName": original_filename
            }
            
            return {
                'success': True,
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            raise IsingClientError(f"OSS upload failed: {str(e)}")
        except KeyError as e:
            raise IsingClientError(f"Invalid signature response, missing field: {str(e)}")