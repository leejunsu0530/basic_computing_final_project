import os
from rich.progress import track

def fix_fullwidth_filenames(target_dir: str):
    # 지워야 할 전각 경로 접두사 (끝에 전각 역슬래시 '＼' 포함)
    prefix_to_remove = "C：＼Users＼leeju＼Projects＼basic_computing_final_project＼test＼.test＼"
    
    # 해당 폴더 안의 모든 파일 탐색
    for filename in track(os.listdir(target_dir)):
        # 파일 이름이 해당 전각 문자열로 시작하는지 확인
        if filename.startswith(prefix_to_remove):
            # 전각 문자열을 지운 새로운 파일명 생성
            new_filename = filename.replace(prefix_to_remove, "")
            
            # 실제 파일의 전체 경로 생성
            old_file_path = os.path.join(target_dir, filename)
            new_file_path = os.path.join(target_dir, new_filename)
            
            try:
                # 파일 이름 변경 실행
                os.rename(old_file_path, new_file_path)
                print(f"[성공] {filename} \n   -> {new_filename}\n")
            except Exception as e:
                print(f"[실패] {filename} 변경 중 에러 발생: {e}\n")
            
# --- 실행 부분 ---
# 파일들이 실제로 저장되어 있는 폴더 경로를 지정하세요.
# (위의 전각 경로상 마지막 폴더인 '.test' 폴더 안을 타겟으로 잡습니다)
target_folder = r"C:\Users\leeju\Projects\basic_computing_final_project\test\.test"

fix_fullwidth_filenames(target_folder)