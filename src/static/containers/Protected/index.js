import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import PropTypes from 'prop-types';

import * as actionCreators from '../../actions/data';

class ProtectedView extends React.Component {
    static propTypes = {
        isFetching: PropTypes.bool.isRequired,
        data: PropTypes.string,
        token: PropTypes.string.isRequired,
        actions: PropTypes.shape({
            dataFetchProtectedData: PropTypes.func.isRequired
        }).isRequired
    };

    static defaultProps = {
        data: ''
    };

    // Note: have to use componentWillMount, if I add this in constructor will get error:
    // Warning: setState(...): Cannot update during an existing state transition (such as within `render`).
    // Render methods should be a pure function of props and state.
    componentWillMount() {
        const token = this.props.token;
        this.props.actions.dataFetchProtectedData(token);
    }

    render() {
        return (
            <div className="protected">
                <div className="container">
                    <h1 className="text-center margin-bottom-medium">Profile</h1>
                    {this.props.isFetching === true ?
                        <p className="text-center">Loading data...</p>
                        :
                        <div>
                            <p>Data received from the server:</p>
                            <div className="margin-top-small">
                                <div className="alert alert-info">
                                    <b>{this.props.data}</b>
                                </div>
                            </div>
                        </div>
                    }
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        data: state.data.data,
        isFetching: state.data.isFetching
    };
};

const mapDispatchToProps = (dispatch) => {
    return {
        actions: bindActionCreators(actionCreators, dispatch)
    };
};

export default connect(mapStateToProps, mapDispatchToProps)(ProtectedView);
export { ProtectedView as ProtectedViewNotConnected };
