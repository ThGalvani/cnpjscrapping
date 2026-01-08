// Configuração da API
const API_BASE = window.location.origin;

// Utilidades
const showLoading = () => document.getElementById('loading').classList.add('active');
const hideLoading = () => document.getElementById('loading').classList.remove('active');

// Formatação de CNPJ
function formatCNPJ(cnpj) {
    const cleaned = cnpj.replace(/\D/g, '');
    if (cleaned.length === 14) {
        return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    return cnpj;
}

// Auto-formatar input de CNPJ
document.getElementById('cnpj')?.addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 14) {
        e.target.value = formatCNPJ(value);
    }
});

// Tabs
function showTab(tabName) {
    // Esconde todas as tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Mostra a tab selecionada
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Mostrar resultado
function showResult(elementId, content, type = 'info') {
    const element = document.getElementById(elementId);
    element.innerHTML = content;
    element.className = `result ${type}`;
}

// Formatar endereço
function formatAddress(endereco) {
    if (!endereco) return 'Não disponível';
    const parts = [
        endereco.logradouro,
        endereco.numero,
        endereco.complemento,
        endereco.bairro,
        endereco.municipio,
        endereco.uf,
        endereco.cep
    ].filter(p => p);
    return parts.join(', ');
}

// Renderizar dados de empresa
function renderCompanyData(data) {
    return `
        <div class="result-card success">
            <h3>${data.razao_social || 'Empresa'}</h3>
            <div class="result-grid">
                <div class="result-item">
                    <strong>CNPJ:</strong>
                    <span>${formatCNPJ(data.cnpj || '')}</span>
                </div>
                <div class="result-item">
                    <strong>Nome Fantasia:</strong>
                    <span>${data.nome_fantasia || 'Não informado'}</span>
                </div>
                <div class="result-item">
                    <strong>Situação:</strong>
                    <span>${data.situacao_cadastral || 'Não disponível'}</span>
                </div>
                <div class="result-item">
                    <strong>CNAE Principal:</strong>
                    <span>${data.cnae_principal?.codigo || ''} - ${data.cnae_principal?.descricao || 'Não informado'}</span>
                </div>
                <div class="result-item">
                    <strong>Data de Abertura:</strong>
                    <span>${data.data_abertura || 'Não informado'}</span>
                </div>
                <div class="result-item">
                    <strong>Porte:</strong>
                    <span>${data.porte || 'Não informado'}</span>
                </div>
                <div class="result-item" style="grid-column: 1 / -1;">
                    <strong>Endereço:</strong>
                    <span>${formatAddress(data.endereco)}</span>
                </div>
                <div class="result-item">
                    <strong>Telefone:</strong>
                    <span>${data.telefone || 'Não informado'}</span>
                </div>
                <div class="result-item">
                    <strong>Email:</strong>
                    <span>${data.email || 'Não informado'}</span>
                </div>
                <div class="result-item">
                    <strong>Capital Social:</strong>
                    <span>${data.capital_social || 'Não informado'}</span>
                </div>
                <div class="result-item">
                    <strong>Fonte:</strong>
                    <span>${data.source || 'Não informado'}</span>
                </div>
            </div>
        </div>
    `;
}

// Verificar status dos dados da Receita ao carregar
async function checkReceitaStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/receita/status`);
        const status = await response.json();

        const alert = document.getElementById('receita-status-alert');
        if (!alert) return;

        if (status.status === 'available') {
            alert.innerHTML = `
                <div style="background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; border-radius: 6px;">
                    <strong style="color: #065f46;">✅ Dados da Receita Federal disponíveis!</strong><br>
                    <span style="color: #047857;">Você pode buscar MEI e ME em qualquer cidade do Brasil.</span><br>
                    <small style="color: #059669;">Arquivos: ${status.files.estabelecimentos} | Cache: ${status.cache.total_cached} consultas</small>
                </div>
            `;
        } else {
            alert.innerHTML = `
                <div style="background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; border-radius: 6px;">
                    <strong style="color: #991b1b;">⚠️ Dados da Receita Federal não disponíveis</strong><br>
                    <span style="color: #b91c1c;">Para usar esta funcionalidade, você precisa baixar os dados públicos da Receita Federal (~3GB).</span><br>
                    <br>
                    <strong style="color: #991b1b;">Como baixar:</strong><br>
                    <code style="background: #fecaca; padding: 5px; border-radius: 3px; color: #7f1d1d;">python -m cnpj_scraper.scrapers.receita_downloader</code><br>
                    <br>
                    <small style="color: #b91c1c;">
                        Fonte oficial: <a href="${status.download_url}" target="_blank" style="color: #7f1d1d; text-decoration: underline;">Receita Federal</a>
                    </small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao verificar status da Receita:', error);
    }
}

// Verifica status ao carregar página
document.addEventListener('DOMContentLoaded', checkReceitaStatus);

// Buscar MEI/ME por região
document.getElementById('mei-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();

    const cidade = document.getElementById('mei-cidade').value;
    const estado = document.getElementById('mei-estado').value;
    const limit = document.getElementById('mei-limit').value;
    const onlyPhone = document.getElementById('mei-only-phone').checked;

    if (!cidade || !estado) {
        showResult('mei-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> Preencha cidade e estado</p>
            </div>
        `, 'error');
        return;
    }

    showLoading();

    try {
        const response = await fetch(
            `${API_BASE}/api/discover/mei-me-by-region?cidade=${encodeURIComponent(cidade)}&estado=${estado}&limit=${limit}&only_with_phone=${onlyPhone}`,
            { method: 'POST' }
        );

        const result = await response.json();

        if (!response.ok) {
            if (response.status === 503) {
                // Dados não disponíveis
                throw new Error(
                    'Dados da Receita Federal não disponíveis. ' +
                    'Execute: python -m cnpj_scraper.scrapers.receita_downloader'
                );
            }
            throw new Error(result.detail || 'Erro ao buscar empresas');
        }

        let html = `
            <div class="result-card success">
                <h3>📊 Resultados - MEI/ME em ${cidade}/${estado}</h3>
                <p><strong>Total encontrado:</strong> ${result.results.total_found}</p>
                <p><strong>Com telefone:</strong> ${result.results.with_phone} (${result.results.percentage_with_phone}%)</p>
                <p><strong>Fonte:</strong> ${result.source}</p>
            </div>
        `;

        if (result.data && result.data.length > 0) {
            // Renderiza empresas
            result.data.forEach(empresa => {
                const hasPhone = empresa.telefone && empresa.telefone.trim();

                html += `
                    <div class="result-card ${hasPhone ? 'success' : ''}">
                        <h3>${empresa.razao_social || empresa.nome_fantasia || 'Empresa'}</h3>
                        <div class="result-grid">
                            <div class="result-item">
                                <strong>CNPJ:</strong>
                                <span>${empresa.cnpj || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>Nome Fantasia:</strong>
                                <span>${empresa.nome_fantasia || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>Porte:</strong>
                                <span style="font-weight: 600; color: #2563eb;">${empresa.porte || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>📞 Telefone:</strong>
                                <span style="font-size: 1.1rem; font-weight: 600; color: #2563eb;">
                                    ${empresa.telefone || 'Não disponível'}
                                </span>
                            </div>
                            <div class="result-item">
                                <strong>📧 Email:</strong>
                                <span>${empresa.email || 'Não disponível'}</span>
                            </div>
                            <div class="result-item" style="grid-column: 1 / -1;">
                                <strong>📍 Endereço:</strong>
                                <span>${empresa.endereco_completo || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>Situação:</strong>
                                <span>${empresa.situacao || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>Tipo:</strong>
                                <span>${empresa.matriz_filial || 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            // Botão de exportar
            html += `
                <div style="margin-top: 20px; text-align: center;">
                    <button onclick="exportMeiPhones()" class="btn btn-secondary">
                        💾 Exportar para CSV
                    </button>
                </div>
            `;

            // Armazena dados globalmente
            window.currentMeiData = result.data;

        } else {
            html += `
                <div class="result-card error">
                    <p>Nenhuma empresa MEI/ME encontrada em ${cidade}/${estado}.</p>
                </div>
            `;
        }

        showResult('mei-result', html, 'success');

    } catch (error) {
        showResult('mei-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> ${error.message}</p>
            </div>
        `, 'error');
    } finally {
        hideLoading();
    }
});

// Função para exportar MEI/ME
function exportMeiPhones() {
    if (!window.currentMeiData || window.currentMeiData.length === 0) {
        alert('Nenhum dado para exportar');
        return;
    }

    // Cria CSV
    const headers = ['CNPJ', 'Razão Social', 'Nome Fantasia', 'Porte', 'Telefone', 'Email', 'Endereço', 'Situação', 'Tipo'];
    const rows = window.currentMeiData.map(empresa => [
        empresa.cnpj || '',
        empresa.razao_social || '',
        empresa.nome_fantasia || '',
        empresa.porte || '',
        empresa.telefone || '',
        empresa.email || '',
        empresa.endereco_completo || '',
        empresa.situacao || '',
        empresa.matriz_filial || ''
    ]);

    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `mei_me_empresas_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Consulta única
document.getElementById('single-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();

    const cnpj = document.getElementById('cnpj').value.replace(/\D/g, '');
    const source = document.getElementById('source').value;

    if (cnpj.length !== 14) {
        showResult('single-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> CNPJ deve ter 14 dígitos</p>
            </div>
        `, 'error');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/cnpj/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cnpj, source })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Erro ao consultar CNPJ');
        }

        const html = renderCompanyData(result.data);
        showResult('single-result', html, 'success');

    } catch (error) {
        showResult('single-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> ${error.message}</p>
            </div>
        `, 'error');
    } finally {
        hideLoading();
    }
});

// Buscar telefones por categoria
document.getElementById('category-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();

    const category = document.getElementById('category').value;
    const source = document.getElementById('category-source').value;
    const onlyWithPhone = document.getElementById('only-with-phone').checked;

    if (!category) {
        showResult('category-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> Selecione uma categoria</p>
            </div>
        `, 'error');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/discover/by-category?category=${category}&source=${source}&collect_phones=true`, {
            method: 'POST'
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Erro ao buscar empresas');
        }

        let html = `
            <div class="result-card success">
                <h3>📊 Resultados - ${category.charAt(0).toUpperCase() + category.slice(1)}</h3>
                <p><strong>Total encontrado:</strong> ${result.total_found}</p>
                <p><strong>Com telefone:</strong> ${result.with_phone}</p>
                <p><strong>Fonte:</strong> ${source}</p>
            </div>
        `;

        if (result.data && result.data.length > 0) {
            // Renderiza empresas com telefones
            result.data.forEach(company => {
                const hasPhone = company.telefone && company.telefone.trim();

                html += `
                    <div class="result-card ${hasPhone ? 'success' : ''}">
                        <h3>${company.razao_social || 'Empresa'}</h3>
                        <div class="result-grid">
                            <div class="result-item">
                                <strong>CNPJ:</strong>
                                <span>${company.cnpj || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>Nome Fantasia:</strong>
                                <span>${company.nome_fantasia || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>📞 Telefone:</strong>
                                <span style="font-size: 1.1rem; font-weight: 600; color: #2563eb;">
                                    ${company.telefone || 'Não disponível'}
                                </span>
                            </div>
                            <div class="result-item">
                                <strong>📧 Email:</strong>
                                <span>${company.email || 'Não disponível'}</span>
                            </div>
                            <div class="result-item" style="grid-column: 1 / -1;">
                                <strong>📍 Endereço:</strong>
                                <span>${company.endereco_completo || 'N/A'}</span>
                            </div>
                            <div class="result-item">
                                <strong>Situação:</strong>
                                <span>${company.situacao || 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            // Adiciona botão de exportar
            html += `
                <div style="margin-top: 20px; text-align: center;">
                    <button onclick="exportPhones()" class="btn btn-secondary">
                        💾 Exportar para CSV
                    </button>
                </div>
            `;

            // Armazena dados globalmente para exportação
            window.currentPhoneData = result.data;

        } else {
            html += `
                <div class="result-card error">
                    <p>Nenhuma empresa encontrada para esta categoria.</p>
                </div>
            `;
        }

        showResult('category-result', html, 'success');

    } catch (error) {
        showResult('category-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> ${error.message}</p>
            </div>
        `, 'error');
    } finally {
        hideLoading();
    }
});

// Função para exportar telefones
function exportPhones() {
    if (!window.currentPhoneData || window.currentPhoneData.length === 0) {
        alert('Nenhum dado para exportar');
        return;
    }

    // Cria CSV
    const headers = ['CNPJ', 'Razão Social', 'Nome Fantasia', 'Telefone', 'Email', 'Endereço', 'Situação'];
    const rows = window.currentPhoneData.map(company => [
        company.cnpj || '',
        company.razao_social || '',
        company.nome_fantasia || '',
        company.telefone || '',
        company.email || '',
        company.endereco_completo || '',
        company.situacao || ''
    ]);

    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `telefones_empresas_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Consulta em lote
document.getElementById('bulk-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();

    const cnpjsText = document.getElementById('cnpjs').value;
    const cnpjs = cnpjsText.split('\n')
        .map(line => line.trim().replace(/\D/g, ''))
        .filter(cnpj => cnpj.length === 14);

    if (cnpjs.length === 0) {
        showResult('bulk-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> Nenhum CNPJ válido fornecido</p>
            </div>
        `, 'error');
        return;
    }

    if (cnpjs.length > 100) {
        showResult('bulk-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> Máximo de 100 CNPJs por consulta</p>
            </div>
        `, 'error');
        return;
    }

    const source = document.getElementById('bulk-source').value;

    // Filtros
    const filters = {};
    const estado = document.getElementById('estado').value.trim();
    const cidade = document.getElementById('cidade').value.trim();
    const cnae = document.getElementById('cnae').value.trim();
    const situacao = document.getElementById('situacao').value.trim();
    const apenasMatriz = document.getElementById('apenas-matriz').checked;

    if (estado) filters.estado = estado;
    if (cidade) filters.cidade = cidade;
    if (cnae) filters.cnae = cnae;
    if (situacao) filters.situacao = situacao;
    if (apenasMatriz) filters.apenas_matriz = true;

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/cnpj/bulk`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cnpjs,
                source,
                filters: Object.keys(filters).length > 0 ? filters : null
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Erro ao consultar CNPJs');
        }

        let html = `
            <div class="result-card success">
                <h3>📊 Resultados da Consulta</h3>
                <p><strong>Total solicitado:</strong> ${result.total_solicitado}</p>
                <p><strong>Total encontrado:</strong> ${result.total_encontrado}</p>
            </div>
        `;

        if (result.data && result.data.length > 0) {
            html += result.data.map(company => renderCompanyData(company)).join('');
        } else {
            html += `
                <div class="result-card error">
                    <p>Nenhuma empresa encontrada com os filtros aplicados.</p>
                </div>
            `;
        }

        showResult('bulk-result', html, 'success');

    } catch (error) {
        showResult('bulk-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> ${error.message}</p>
            </div>
        `, 'error');
    } finally {
        hideLoading();
    }
});

// Estatísticas
async function loadStats() {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();

        let html = '<div class="stats-grid">';

        // Stats dos scrapers
        for (const [source, data] of Object.entries(stats.scrapers)) {
            html += `
                <div class="stat-card">
                    <div class="number">${data.requests_made || 0}</div>
                    <div class="label">${source} - Requisições</div>
                </div>
                <div class="stat-card">
                    <div class="number">${data.successful_requests || 0}</div>
                    <div class="label">${source} - Sucessos</div>
                </div>
                <div class="stat-card">
                    <div class="number">${data.cached_responses || 0}</div>
                    <div class="label">${source} - Cache</div>
                </div>
            `;
        }

        // Stats do cache
        if (stats.cache) {
            html += `
                <div class="stat-card">
                    <div class="number">${stats.cache.total_cached || 0}</div>
                    <div class="label">Total em Cache</div>
                </div>
                <div class="stat-card">
                    <div class="number">${stats.cache.active || 0}</div>
                    <div class="label">Cache Ativo</div>
                </div>
                <div class="stat-card">
                    <div class="number">${stats.cache.total_size_kb || 0} KB</div>
                    <div class="label">Tamanho do Cache</div>
                </div>
            `;
        }

        html += '</div>';

        showResult('stats-result', html);

    } catch (error) {
        showResult('stats-result', `
            <div class="result-card error">
                <p><strong>Erro:</strong> ${error.message}</p>
            </div>
        `, 'error');
    } finally {
        hideLoading();
    }
}

// Limpar cache
async function clearCache() {
    if (!confirm('Tem certeza que deseja limpar todo o cache?')) {
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/cache/clear`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            alert(`Cache limpo com sucesso! ${result.files_removed} arquivos removidos.`);
            loadStats();
        }

    } catch (error) {
        alert(`Erro ao limpar cache: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Carregar estatísticas ao abrir a aba
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (this.textContent.includes('Estatísticas')) {
            loadStats();
        }
    });
});
