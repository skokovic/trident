import React from 'react';
import { push } from 'react-router-redux';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import './style.scss';
import reactLogo from './images/react-logo.png';
import reduxLogo from './images/redux-logo.png';
import tridentLogo from './images/trident-image.jpg'

class HomeView extends React.Component {
    static propTypes = {
        statusText: PropTypes.string,
        userName: PropTypes.string,
        dispatch: PropTypes.func.isRequired
    };

    static defaultProps = {
        statusText: '',
        userName: ''
    };

    goToProtected = () => {
        this.props.dispatch(push('/protected'));
    };

    render() {
        return (
            <div className="container">
                <div className="margin-top-medium text-center">
                    <img className="page-logo margin-bottom-medium"
                        src={tridentLogo}
                        alt="ReactJs"
                    />
                </div>
                <div className="text-center">
                    <h1>Trident</h1>
                    <h4>Hello, {this.props.userName || 'guest'}.</h4>
                </div>
                <div className="margin-top-medium text-center">
                    <p>Go to your <a onClick={this.goToProtected}><b>profile</b></a>.</p>
                </div>
                <div className="margin-top-medium">
                    {this.props.statusText ?
                        <div className="alert alert-info">
                            {this.props.statusText}
                        </div>
                        :
                        null
                    }
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        userName: state.auth.userName,
        statusText: state.auth.statusText
    };
};

export default connect(mapStateToProps)(HomeView);
export { HomeView as HomeViewNotConnected };
