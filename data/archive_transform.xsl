<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"/>

    <xsl:template match="/">
        <html lang="uk">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
            <title>Електронний архів факультету — Науково-методичні матеріали</title>
            <style type="text/css">
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: #f4f6f9;
                    color: #2d3748;
                    margin: 0;
                    padding: 30px;
                }
                .container {
                    max-width: 1600px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    padding: 30px;
                }
                h1 {
                    color: #1a365d;
                    font-size: 24px;
                    margin-bottom: 8px;
                    border-bottom: 2px solid #3182ce;
                    padding-bottom: 12px;
                }
                .subtitle {
                    color: #718096;
                    font-size: 14px;
                    margin-bottom: 24px;
                }
                .summary {
                    background-color: #ebf8ff;
                    border-left: 4px solid #3182ce;
                    padding: 10px 16px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                    font-size: 14px;
                    color: #2b6cb0;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                    font-size: 13px;
                }
                th {
                    background-color: #2b6cb0;
                    color: #ffffff;
                    font-weight: 600;
                    text-align: left;
                    padding: 12px 10px;
                    border: 1px solid #cbd5e0;
                }
                td {
                    padding: 10px;
                    border: 1px solid #e2e8f0;
                    vertical-align: top;
                }
                tr:nth-child(even) {
                    background-color: #f7fafc;
                }
                tr:hover {
                    background-color: #edf2f7;
                }
                .badge {
                    display: inline-block;
                    padding: 2px 6px;
                    font-size: 11px;
                    border-radius: 4px;
                    background-color: #e2e8f0;
                    color: #4a5568;
                    margin: 2px;
                    white-space: nowrap;
                }
                .badge-type {
                    background-color: #feebc8;
                    color: #7b341e;
                    font-weight: 600;
                }
                .badge-id {
                    background-color: #e9d8fd;
                    color: #553c9a;
                    font-weight: bold;
                }
                .badge-attr {
                    background-color: #c6f6d5;
                    color: #22543d;
                }
                .title-cell {
                    font-weight: bold;
                    color: #2c5282;
                }
                .annotation {
                    color: #4a5568;
                    font-style: italic;
                    font-size: 12px;
                    margin-top: 4px;
                }
                .footer {
                    margin-top: 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #a0aec0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1><xsl:value-of select="FacultyArchive/@name"/></h1>
                <div class="subtitle">Звіт сформовано засобами XSLT-трансформації</div>
                
                <div class="summary">
                    Всього знайдено записів у архіві: <strong><xsl:value-of select="count(FacultyArchive/Material)"/></strong>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th style="width: 5%;">ID</th>
                            <th style="width: 20%;">Назва матеріалу</th>
                            <th style="width: 15%;">Автор</th>
                            <th style="width: 15%;">Підрозділ / Кафедра</th>
                            <th style="width: 8%;">Вид</th>
                            <th style="width: 6%;">Обсяг</th>
                            <th style="width: 8%;">Дата</th>
                            <th style="width: 13%;">Динамічні атрибути</th>
                            <th style="width: 10%;">Анотація</th>
                        </tr>
                    </thead>
                    <tbody>
                        <xsl:for-each select="FacultyArchive/Material">
                            <tr>
                                <td>
                                    <span class="badge badge-id"><xsl:value-of select="@id"/></span>
                                </td>
                                <td class="title-cell">
                                    <xsl:value-of select="Title"/>
                                    <xsl:if test="Keywords">
                                        <div style="font-size: 11px; color: #718096; margin-top: 4px;">
                                            <em>Теги: <xsl:value-of select="Keywords"/></em>
                                        </div>
                                    </xsl:if>
                                </td>
                                <td>
                                    <strong><xsl:value-of select="Author"/></strong>
                                </td>
                                <td>
                                    <div><strong>Ф-т:</strong> <xsl:value-of select="Department"/></div>
                                    <div><strong>Каф:</strong> <xsl:value-of select="Chair"/></div>
                                </td>
                                <td>
                                    <span class="badge badge-type"><xsl:value-of select="@type"/></span>
                                </td>
                                <td style="text-align: center;">
                                    <xsl:value-of select="Volume"/> с.
                                </td>
                                <td>
                                    <xsl:value-of select="CreatedDate"/>
                                </td>
                                <td>
                                    <xsl:for-each select="@*[name() != 'id' and name() != 'type']">
                                        <div class="badge badge-attr">
                                            <xsl:value-of select="name()"/>: <xsl:value-of select="."/>
                                        </div>
                                    </xsl:for-each>
                                </td>
                                <td>
                                    <div class="annotation"><xsl:value-of select="Annotation"/></div>
                                </td>
                            </tr>
                        </xsl:for-each>
                    </tbody>
                </table>

                <div class="footer">
                    Електронний архів факультету &#169; 2026. Система обробки XML-документів.
                </div>
            </div>
        </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
