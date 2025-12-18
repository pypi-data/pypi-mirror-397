#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BrookJI lllabmaster@gmail.com

"""
jsonl_to_html_md.py

功能：
- 将 jsonl 文件转换为支持 Markdown 渲染的 HTML 表格
- 支持指定展示字段（列名）
- 默认展示所有字段
- 前端使用 marked.js + highlight.js 渲染 Markdown

参数（argparse）：
--input / -i   : jsonl 文件路径（必填）
--output / -o  : 输出 html 文件路径（必填）
--fields / -f  : 逗号分隔的字段名（可选，默认全部字段）

示例：
python jsonl_to_html_md.py -i data.jsonl -o output.html
python jsonl_to_html_md.py -i data.jsonl -o output.html -f prompt,response,analysis
"""

import json
import html
import argparse
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\">
<title>JSONL Markdown Viewer</title>

<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/datatables.net-dt@1.13.8/css/jquery.dataTables.min.css\">
<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.min.css\">

<script src=\"https://code.jquery.com/jquery-3.7.1.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/datatables.net@1.13.8/js/jquery.dataTables.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/marked/marked.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/common.min.js\"></script>

<style>
body {{
  margin: 16px;
  font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Helvetica, Arial;
}}

#tbl {{
  width: 100% !important;
  border-collapse: collapse;
}}

#tbl th {{
  background-color: #f2f2f2;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #ddd;
}}

#tbl td {{
  padding: 12px;
  border-bottom: 1px solid #eee;
  vertical-align: top;
}}

.md-cell {{
  max-width: 800px;
  min-width: 200px;
  white-space: normal;
  word-wrap: break-word;
  overflow-wrap: break-word;
}}

.md-cell pre {{
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  max-height: 400px;
}}

.md-cell code:not(pre code) {{
  background-color: #f6f8fa;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 90%;
}}

.md-cell table {{
  border-collapse: collapse;
  margin: 8px 0;
}}

.md-cell th, .md-cell td {{
  border: 1px solid #ddd;
  padding: 6px 8px;
}}

.dataTables_wrapper {{
  margin-top: 20px;
}}

.dataTables_length,
.dataTables_filter,
.dataTables_info,
.dataTables_paginate {{
  margin: 10px 0;
}}
</style>
</head>

<body>
<h2>JSONL Data Viewer</h2>

<table id=\"tbl\" class=\"display\">
<thead>
<tr>
{thead}
</tr>
</thead>
<tbody>
{tbody}
</tbody>
</table>

<script>
// 配置 marked.js
marked.setOptions({{
  breaks: true,
  gfm: true,
  highlight: function(code, lang) {{
    if (lang && hljs.getLanguage(lang)) {{
      try {{
        return hljs.highlight(code, {{ language: lang }}).value;
      }} catch (err) {{}}
    }}
    try {{
      return hljs.highlightAuto(code).value;
    }} catch (err) {{
      return code;
    }}
  }}
}});

// 初始化 DataTable
$(document).ready(function() {{
  const table = $('#tbl').DataTable({{
    pageLength: 25,
    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    scrollX: true,
    scrollCollapse: true,
    autoWidth: false,
    columnDefs: [
      {{
        targets: '_all',
        className: 'md-cell',
        width: '200px'
      }}
    ],
    language: {{
      search: "搜索:",
      lengthMenu: "显示 _MENU_ 条记录",
      info: "显示第 _START_ 到 _END_ 条记录，共 _TOTAL_ 条",
      paginate: {{
        first: "首页",
        last: "末页",
        next: "下一页",
        previous: "上一页"
      }}
    }}
  }});

  // 渲染 Markdown
  function renderMarkdownInTable() {{
    $('.md-cell').each(function() {{
      const $cell = $(this);
      // 检查是否已渲染
      if ($cell.data('rendered')) return;
      
      try {{
        const rawText = $cell.text().trim();
        if (!rawText) return;
        
        // 尝试解析 JSON，如果失败则直接显示文本
        let content;
        try {{
          content = JSON.parse(rawText);
        }} catch (e) {{
          content = rawText;
        }}
        
        // 如果是对象或数组，转换为格式化字符串
        if (typeof content === 'object' && content !== null) {{
          content = JSON.stringify(content, null, 2);
        }}
        
        // 渲染 Markdown
        const htmlContent = marked.parse(content.toString());
        $cell.html(htmlContent);
        $cell.data('rendered', true);
        
        // 应用 highlight.js 语法高亮
        $cell.find('pre code').each(function() {{
          hljs.highlightElement(this);
        }});
      }} catch (err) {{
        console.error('渲染失败:', err);
      }}
    }});
  }}

  // 初始渲染
  renderMarkdownInTable();
  
  // 表格重绘时重新渲染
  table.on('draw', function() {{
    setTimeout(renderMarkdownInTable, 100);
  }});
  
  // 分页时重新渲染
  table.on('page', function() {{
    setTimeout(renderMarkdownInTable, 100);
  }});
}});
</script>

</body>
</html>
"""


def load_jsonl(path: Path):
    """加载 JSONL 文件"""
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"警告：跳过无法解析的行: {e}")
                continue
    return rows


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="将 JSONL 文件转换为支持 Markdown 渲染的 HTML 表格"
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        type=Path,
        help='输入的 JSONL 文件路径'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        type=Path,
        help='输出的 HTML 文件路径'
    )

    parser.add_argument(
        '-f', '--fields',
        default=None,
        help='要显示的字段名，用逗号分隔（默认显示所有字段）'
    )

    return parser.parse_args()


def escape_html_for_table(text):
    """为表格单元格转义 HTML"""
    if text is None:
        return ""
    return html.escape(str(text))


def main():
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"输入文件不存在: {args.input}")

    # 加载数据
    data = load_jsonl(args.input)
    if not data:
        raise ValueError('JSONL 文件为空或无法解析')

    # 确定要显示的字段
    if args.fields:
        fields = [f.strip() for f in args.fields.split(',') if f.strip()]
        # 验证字段是否存在
        for field in fields:
            if not any(field in row for row in data):
                print(f"警告：字段 '{field}' 在数据中不存在")
    else:
        # 收集所有字段
        fields = []
        for row in data:
            for key in row.keys():
                if key not in fields:
                    fields.append(key)

    print(f"发现 {len(data)} 条记录")
    print(f"显示字段: {', '.join(fields)}")

    # 生成表头
    thead = '\n'.join(f'<th>{escape_html_for_table(f)}</th>' for f in fields)

    # 生成表格内容
    tbody_rows = []
    for row in data:
        tds = []
        for field in fields:
            # 获取字段值，如果不存在则显示空字符串
            val = row.get(field, "")
            
            # 对于复杂类型，转换为 JSON 字符串
            if isinstance(val, (dict, list)):
                cell_content = json.dumps(val, ensure_ascii=False, indent=2)
            else:
                cell_content = str(val) if val is not None else ""
            
            # 转义 HTML 并存储原始内容在 data 属性中
            escaped_content = escape_html_for_table(cell_content)
            tds.append(f'<td class="md-cell" data-raw="{escape_html_for_table(cell_content)}">{escaped_content}</td>')
        
        tbody_rows.append('<tr>' + ''.join(tds) + '</tr>')

    # 生成完整的 HTML
    html_content = HTML_TEMPLATE.format(
        thead=thead,
        tbody='\n'.join(tbody_rows)
    )

    # 确保输出目录存在
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    with args.output.open('w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML 文件已生成: {args.output}")
    print(f"文件大小: {args.output.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    main()